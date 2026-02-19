import React from 'react';
import { useNavigate } from 'react-router-dom';
import { logout, getUser } from '../../services/auth';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = async () => {
    await logout();
    navigate('/admin/login');
  };

  return (
    <div className="admin-layout">
      <header className="admin-header">
        <div className="admin-header-left">
          <h1>Panel de Administracion</h1>
          <span className="admin-subtitle">Zaragoza Historica</span>
        </div>
        <div className="admin-header-right">
          <span className="admin-user">
            {user?.username} ({user?.role})
          </span>
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            Ver sitio
          </button>
          <button className="btn btn-logout" onClick={handleLogout}>
            Cerrar sesion
          </button>
        </div>
      </header>
      <main className="admin-main">
        {children}
      </main>
    </div>
  );
};
