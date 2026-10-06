import { useState, useEffect } from 'react';
import styles from './RegistryPage.module.css';

const LABELS_MAP = {
  currency: 'Валюта',
  inn: 'ИНН',
  ogrn: 'ОГРН',
  kpp: 'КПП',
  number: 'Номер договора',
  date: 'Дата договора',
  amount: 'Сумма',
  parties: 'Стороны',
  subject: 'Предмет договора',
  term: 'Срок действия',
};

export default function RegistryPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDoc, setSelectedDoc] = useState(null);

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
    <section className={styles.pageContainer}>
      <div className={styles.tableCard}>
        <h2 className={styles.title}>Реестр договоров</h2>

        {loading && <p className={styles.statusText}>Загрузка данных из базы...</p>}
        {error && <p className={styles.errorText}>{error}</p>}

        {!loading && !error && documents.length === 0 && (
          <p className={styles.statusText}>В реестре пока нет сохраненных договоров.</p>
        )}

        {!loading && !error && documents.length > 0 && (
          <div className={styles.tableWrapper}>
            <table className={styles.styledTable}>
              <thead>
                <tr>
                  <th style={{ width: '10%' }}>№</th>
                  <th>Документ (Имя файла)</th>
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
                    <tr
                    key={doc.id || index}
                    className={styles.clickableRow}
                    onClick={() => setSelectedDoc(doc)}
                  >
                    <td className={styles.numberCell}>{index + 1}</td>
                    <td>
                      <div className={styles.docNameWrapper}>
                        <span className={styles.docIcon}>📄</span>
                        <span className={styles.docText}>
                          {doc.filename ? doc.filename : `Сохраненный договор #${doc.document_id || index + 1}`}
                        </span>
                      </div>
                    </td>
                    <td>{attrs.number || '—'}</td>
                      <td>{attrs.date || '—'}</td>
                      <td className={styles.partiesCell}>
                        {Array.isArray(attrs.parties) ? attrs.parties.join('; ') : attrs.parties || '—'}
                      </td>
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

      {selectedDoc && (
        <div className={styles.modalOverlay} onClick={() => setSelectedDoc(null)}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>Данные документа</h3>
              <button className={styles.closeBtn} onClick={() => setSelectedDoc(null)}>
                ✖
              </button>
            </div>

            <div className={styles.modalBody}>
              {(() => {
                const attrs = selectedDoc.attributes || {};
                return (
                  <>
                    <div className={styles.fieldsList}>
                      {renderField('Номер договора', attrs.number)}
                      {renderField('Дата договора', attrs.date)}
                      {renderField('Сумма', attrs.amount)}
                      {renderField('Стороны', attrs.parties)}

                      {attrs.additional_data &&
                        Object.entries(attrs.additional_data).map(([key, val]) => (
                          renderField(LABELS_MAP[key] || key, val)
                        ))}
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}