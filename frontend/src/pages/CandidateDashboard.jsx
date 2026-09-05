import { useState, useEffect, useContext, useCallback } from 'react';
import { Button, Empty, Modal, Spin, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import UploadCvForm from '../components/UploadCvForm';

function formatDate(value) {
  if (!value) return '';
  const d = new Date(value);
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

function scoreTier(score) {
  if (score == null) return { color: 'var(--color-ink-muted)', label: 'Chưa có kết quả' };
  if (score >= 80) return { color: 'var(--color-match-high)', label: 'Phù hợp cao' };
  if (score >= 50) return { color: 'var(--color-match-mid)', label: 'Phù hợp trung bình' };
  return { color: 'var(--color-match-low)', label: 'Phù hợp thấp' };
}

export default function CandidateDashboard() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const navigate = useNavigate();
  const { logout, user } = useContext(AuthContext);

  const loadApplications = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/candidates/my-applications');
      setApplications(res.data || []);
    } catch (err) {
      console.error('Lỗi tải danh sách ứng tuyển:', err);
      message.error('Không tải được danh sách các vị trí đã ứng tuyển.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadApplications();
  }, [loadApplications]);

  const handleUploadSuccess = (candidateId) => {
    setUploadModalOpen(false);
    loadApplications();
    navigate(`/candidate/matches/${candidateId}`);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-paper)' }}>
      <header
        style={{
          borderBottom: '1px solid var(--color-border)',
          padding: '20px 40px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <p style={{ margin: 0, fontSize: 13, color: 'var(--color-ink-muted)' }}>Xin chào</p>
          <h2 style={{ fontSize: 22 }}>{user?.fullName || user?.name || 'Ứng viên'}</h2>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadModalOpen(true)}>
            Ứng tuyển vị trí khác
          </Button>
          <Button onClick={logout}>Đăng xuất</Button>
        </div>
      </header>

      <main style={{ maxWidth: 760, margin: '0 auto', padding: '40px 24px' }}>
        <h1 style={{ fontSize: 28, marginBottom: 24 }}>Các vị trí đã ứng tuyển</h1>

        <Spin spinning={loading}>
          {applications.length === 0 && !loading ? (
            <div style={{ background: 'var(--color-paper-raised)', border: '1px solid var(--color-border)', borderRadius: 10, padding: 48 }}>
              <Empty description="Bạn chưa ứng tuyển vị trí nào">
                <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadModalOpen(true)}>
                  Tải CV để ứng tuyển
                </Button>
              </Empty>
            </div>
          ) : (
            <div style={{ border: '1px solid var(--color-border)', borderRadius: 10, background: 'var(--color-paper-raised)', overflow: 'hidden' }}>
              {applications.map((app, idx) => {
                const tier = scoreTier(app.topScore);
                return (
                  <div
                    key={app.id}
                    onClick={() => navigate(`/candidate/matches/${app.id}`)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '22px 28px',
                      borderTop: idx === 0 ? 'none' : '1px solid var(--color-border)',
                      cursor: 'pointer',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = '#F8F9F5')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <div>
                      <div style={{ fontFamily: 'var(--font-display)', fontSize: 19, fontWeight: 600, marginBottom: 4 }}>
                        {app.position || 'Chưa xác định vị trí'}
                      </div>
                      <div style={{ fontSize: 13, color: 'var(--color-ink-muted)' }}>
                        Nộp ngày {formatDate(app.createdAt)} · {app.matchCount} vị trí phù hợp được tìm thấy
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', minWidth: 100 }}>
                      <div className="score-figure" style={{ fontSize: 28, color: tier.color, lineHeight: 1 }}>
                        {app.topScore != null ? `${Number(app.topScore).toFixed(0)}%` : '—'}
                      </div>
                      <div style={{ fontSize: 11, color: tier.color }}>{tier.label}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Spin>
      </main>

      <Modal
        title="Ứng tuyển vị trí khác"
        open={uploadModalOpen}
        onCancel={() => setUploadModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <UploadCvForm onSuccess={handleUploadSuccess} />
      </Modal>
    </div>
  );
}
