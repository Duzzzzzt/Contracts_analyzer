import { useState, useEffect } from 'react';
import styles from './RegistryPage.module.css';

export default function RegistryPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Запрашиваем список документов с бэкенда при загрузке страницы
  useEffect(() => {
    const fetchRegistry = async () => {
      try {
        const response = await fetch('http://localhost:8000/registry');

        if (!response.ok) {
          throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const data = await response.json();
        setDocuments(data.items);
      } catch (err) {
        console.error('Ошибка загрузки реестра:', err);
        setError('Не удалось загрузить данные реестра. Возможно, бэкенд недоступен.');
      } finally {
        setLoading(false);
      }
    };

    fetchRegistry();
  }, []);

  return (
    <section className={styles.pageContainer}>
      <div className={styles.tableCard}>
        <h2 className={styles.title}>Реестр обработанных договоров</h2>

        {loading && (
          <p className={styles.statusText}>Загрузка данных из базы...</p>
        )}

        {error && (
          <p className={styles.errorText}>{error}</p>
        )}

        {!loading && !error && documents.length === 0 && (
          <p className={styles.statusText}>В реестре пока нет сохраненных договоров.</p>
        )}

        {!loading && !error && documents.length > 0 && (
          <div className={styles.tableWrapper}>
            <table className={styles.styledTable}>
              <thead>
                <tr>
                  <th>№</th>
                  <th>Номер договора</th>
                  <th>Дата</th>
                  <th>Стороны</th>
                  <th>Сумма</th>
                  <th>ИНН</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc, index) => {
                  const attrs = doc.attributes || {};
                  const additional = attrs.additional_data || {};

                  return (
                    <tr key={doc.id || index}>
                      <td>{index + 1}</td>
                      <td>{attrs.number || '—'}</td>
                      <td>{attrs.date || '—'}</td>
                      <td className={styles.partiesCell}>{attrs.parties || '—'}</td>
                      <td className={styles.amountCell}>
                        {attrs.amount ? `${attrs.amount} ₽` : '—'}
                      </td>
                      <td>
                        {Array.isArray(additional.inn)
                          ? additional.inn.join('; ')
                          : additional.inn || '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}