import styles from './Header.module.css';
import { NavLink } from 'react-router-dom';

export default function Header() {
  return (
    <header>
      <div>
        <span className={styles.logo}>DocAnalyzer</span>
        <ul>
          <li>
            <NavLink to="/upload" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
              Загрузка и анализ
            </NavLink>
          </li>
          <li>
            <NavLink to="/registry" className={({ isActive }) => isActive ? styles.activeLink : styles.link}>
              Реестр договоров
            </NavLink>
          </li>
        </ul>
      </div>
    </header>
  );
}
