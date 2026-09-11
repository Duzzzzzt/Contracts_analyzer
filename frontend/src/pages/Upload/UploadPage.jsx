import { useState } from 'react';
import UploadForm from '../../components/features/UploadForm/UploadForm';
import styles from './UploadPage.module.css';

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState('idle');
  const [extractedData, setExtractedData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setStatus('idle');
    setErrorMessage('');
    setExtractedData(null);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setStatus('idle');
    setExtractedData(null);
    setErrorMessage('');
  };

  const handleSubmit = async () => {
    if (!selectedFile) return;

    setStatus('loading');
    setErrorMessage('');
    setExtractedData(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      let responseData = await response.json();

      if (!responseData.attributes && responseData.id) {
        const docResponse = await fetch(`http://localhost:8000/documents/${responseData.id}`);
        if (docResponse.ok) {
          responseData = await docResponse.json();
        }
      }

      const attrs = responseData.attributes || {};

      const hasFields = Object.keys(attrs).some((key) => {
        const val = attrs[key];
        return val && (!Array.isArray(val) || val.length > 0);
      });

      if (hasFields) {
        setExtractedData(attrs);
        setStatus('success');
      } else {
        setStatus('pending');
      }

    } catch (err) {
      console.error('Ошибка обработки:', err);
      setErrorMessage(`Не удалось обработать документ: ${err.message}`);
      setStatus('error');
    }
  };

  const renderField = (label, value) => {
    if (!value || (Array.isArray(value) && value.length === 0)) return null;

    return (
      <div className={styles.fieldRow} key={label}>
        <span className={styles.fieldLabel}>{label}:</span>
        <span className={styles.fieldValue}>
          {Array.isArray(value) ? value.join('; ') : value}
        </span>
      </div>
    );
  };

  return (
    <section className={styles.sectionContainer}>

      <div className={styles.leftPanel}>
        <div className={styles.form}>
          { }
          <UploadForm onFileSelect={handleFileSelect} selectedFile={selectedFile} />
        </div>
        <div className={styles.buttonGroup}>
          <button
            className={styles.actionBtn}
            onClick={handleSubmit}
            disabled={!selectedFile || status === 'loading'}
          >
            Отправить
          </button>
          <button
            className={styles.actionBtn}
            onClick={handleReset}
            disabled={!selectedFile || status === 'loading'}
          >
            Сбросить
          </button>
        </div>
      </div>

      <div className={styles.rightPanel}>
        <div className={`${styles.result} ${status === 'success' && extractedData ? styles.hasContent : ''}`}>
          {status === 'idle' && (
            <p className={styles.placeholderText}>
              {selectedFile
                ? `Файл "${selectedFile.name}" выбран. Нажмите "Отправить" для извлечения данных.`
                : 'Загрузите документ слева для извлечения данных'
              }
            </p>
          )}

          {status === 'loading' && (
            <p className={styles.loadingText}>
              Нейронная сеть анализирует договор...
            </p>
          )}

          {status === 'pending' && (
            <p className={styles.placeholderText}>
              Файл принят сервером, но бэкенд пока не вернул извлеченные поля (объект attributes пуст).
            </p>
          )}

          {status === 'success' && extractedData && (
            <div className={styles.fieldsContainer}>
              <h3 className={styles.resultTitle}>Извлеченные данные</h3>
              <div className={styles.fieldsList}>
                {renderField('Номер договора', extractedData.number)}
                {renderField('Дата', extractedData.date)}
                {renderField('Сумма', extractedData.amount)}
                {renderField('Стороны', extractedData.parties)}

                {extractedData.additional_data &&
                  Object.entries(extractedData.additional_data).map(([key, val]) => (
                    renderField(key, val)
                  ))}
              </div>
            </div>
          )}

          {status === 'error' && (
            <p className={styles.errorText}>
              {errorMessage}
            </p>
          )}
        </div>
        <div className={styles.buttonGroup}>
          <button
            className={styles.actionBtn}
            disabled={status !== 'success'}
          >
            Сохранить в реестр
          </button>
        </div>
      </div>

    </section>
  );
}