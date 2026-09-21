import { useState, useEffect } from 'react';
import styles from './UploadForm.module.css';

export default function UploadForm({ onFileSelect, selectedFile }) {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      // eslint-disable-next-line
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [selectedFile]);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!selectedFile) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (selectedFile) return;

    const files = e.dataTransfer.files;
    if (files && files.length > 0 && onFileSelect) {
      onFileSelect(files[0]);
    }
  };

  const handleChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0 && onFileSelect) {
      onFileSelect(files[0]);
    }
  };

  if (selectedFile) {
    return (
      <div className={styles.previewContainer}>
        {selectedFile.type === 'application/pdf' ? (
          <iframe
            src={`${previewUrl}#toolbar=0`}
            className={styles.previewFrame}
            title="Предпросмотр документа"
          />
        ) : (
          <div className={styles.fileCard}>
            <span className={styles.fileIcon}>📄</span>
            <p className={styles.fileName}>{selectedFile.name}</p>
            <p className={styles.fileNote}>
              Предпросмотр недоступен для этого формата, но файл готов к отправке.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <label
      className={`${styles.dropZone} ${isDragging ? styles.dragging : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className={styles.content}>
        <p className={styles.text}>
          {isDragging
            ? 'Отпустите файл для выбора'
            : 'Перетащите договор сюда или нажмите для выбора'
          }
        </p>
      </div>

      <input
        type='file'
        className={styles.inputHidden}
        onChange={handleChange}
        accept='.pdf,.doc,.docx,.txt'
      />
    </label>
  );
}