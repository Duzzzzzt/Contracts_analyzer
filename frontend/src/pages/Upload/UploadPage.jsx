import { useState } from 'react';
import UploadForm from '../../components/features/UploadForm/UploadForm';
import styles from './UploadPage.module.css';

export default function UploadPage() {
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'success' | 'error'
  const [extractedText, setExtractedText] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileSelect = async (file) => {
    setStatus('loading');
    setErrorMessage('');
    setExtractedText('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // отправка файла на бэкенд
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const data = await response.json();

      // сырой текст
      const rawText = data.raw_text || data.text || data.content || data.description;

      if (rawText) {
        setExtractedText(rawText);
      } else {
        setExtractedText(JSON.stringify(data, null, 2));
      }
      setStatus('success');
    } catch (err) {
      console.error('Ошибка извлечения текста:', err);
      setErrorMessage(`Не удалось извлечь текст: ${err.message}`);
      setStatus('error');
    }
  };

  return (
    <section className={styles.sectionContainer}>
      <div className={styles.form}>
        <UploadForm onFileSelect={handleFileSelect} />
      </div>
      <div className={styles.result}>
        {status === 'idle' && (
          <p style={{ color: '#777', textAlign: 'center', margin: 'auto' }}>
            Загрузите документ слева для извлечения текста
          </p>
        )}

        {status === 'loading' && (
          <p style={{ textAlign: 'center', margin: 'auto' }}>
            Идет извлечение сырого текста из документа...
          </p>
        )}

        {status === 'success' && (
          <pre style={{
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            margin: 0,
            width: '100%',
            height: '100%',
            overflowY: 'auto'
          }}>
            {extractedText}
          </pre>
        )}

        {status === 'error' && (
          <p style={{ color: '#d9534f', textAlign: 'center', margin: 'auto' }}>
            {errorMessage}
          </p>
        )}
      </div>
    </section>
  );
}