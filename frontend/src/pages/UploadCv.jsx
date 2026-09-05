import { useContext } from 'react';
import { Button, Card } from 'antd';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import UploadCvForm from '../components/UploadCvForm';

export default function UploadCv() {
  const navigate = useNavigate();
  const { logout } = useContext(AuthContext);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-paper)', padding: '40px 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', maxWidth: 500, margin: '0 auto 16px' }}>
         <Button onClick={logout}>Đăng xuất</Button>
      </div>

      <Card style={{ maxWidth: 500, margin: '0 auto', border: '1px solid var(--color-border)' }}>
        <h2 style={{ fontSize: 22, marginBottom: 16 }}>Upload CV</h2>
        <UploadCvForm onSuccess={(candidateId) => navigate(`/candidate/matches/${candidateId}`)} />
      </Card>
    </div>
  );
}
