import { useState } from 'react';
import styles from './UploadForm.module.css';

export default function UploadForm({ onFileSelect }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
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
            ? 'Отпустите файл для загрузки'
            : 'Перетащите договор сюда или нажмите для выбора'
          }
        </p>
      </div>

      <input
        type='file'
        className={styles.inputHidden}
        onChange={handleChange}
        accept='.pdf,.doc,.docx'
      />
    </label>
  );
}