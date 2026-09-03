import { useState } from 'react';
import UploadForm from '../../components/features/UploadForm/UploadForm';
import styles from './UploadPage.module.css';

export default function UploadPage() {
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'pending' | 'success' | 'error'
  const [extractedData, setExtractedData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileSelect = async (file) => {
    setStatus('loading');
    setErrorMessage('');
    setExtractedData(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      let responseData = await response.json();

      // если вернулся только ID, пробуем запросить данные документа
      if (!responseData.attributes && responseData.id) {
        const docResponse = await fetch(`http://localhost:8000/documents/${responseData.id}`);
        if (docResponse.ok) {
          responseData = await docResponse.json();
        }
      }

      const attrs = responseData.attributes || {};

      // проверка, есть ли внутри attributes хотя бы одно непустое значение
      const hasFields = Object.keys(attrs).some((key) => {
        const val = attrs[key];
        return val && (!Array.isArray(val) || val.length > 0);
      });

      if (hasFields) {
        setExtractedData(attrs);
        setStatus('success');
      } else {
        // если attributes пуст или отсутствуют распарсенные данные
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
      <div className={styles.form}>
        <UploadForm onFileSelect={handleFileSelect} />
      </div>

      <div className={styles.result}>
        {status === 'idle' && (
          <p className={styles.placeholderText}>
            Загрузите документ слева для извлечения данных
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
    </section>
  );
}