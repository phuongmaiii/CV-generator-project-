import { useState, useEffect } from 'react';
import { Card, Descriptions, Button, message, Spin } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftOutlined } from '@ant-design/icons';
import api from '../services/api';

export default function CandidateDetails() {
  const { id } = useParams();
  const jobPostingId = new URLSearchParams(window.location.search).get('jobPostingId');
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCandidateDetails = async () => {
      try {
        // Gọi đúng API lấy chi tiết 1 ứng viên
        const suffix = jobPostingId ? `?jobPostingId=${encodeURIComponent(jobPostingId)}` : '';
        const res = await api.get(`/candidates/${id}${suffix}`);
        setCandidate(res.data);
      } catch (error) {
        message.error('Không thể tải thông tin chi tiết ứng viên.');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCandidateDetails();
    }
  }, [id, jobPostingId]);

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  return (
    <Card
      title="Hồ Sơ Chi Tiết Ứng Viên"
      style={{ maxWidth: 800, margin: '40px auto' }}
      extra={
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
          Quay lại
        </Button>
      }
    >
      {candidate ? (
        <Descriptions bordered column={1}>
          <Descriptions.Item label="Mã Ứng Viên">{candidate.id}</Descriptions.Item>
          <Descriptions.Item label="Họ và Tên"><b>{candidate.fullName}</b></Descriptions.Item>
          <Descriptions.Item label="Email">{candidate.email}</Descriptions.Item>
          <Descriptions.Item label="Ngành nghề AI Phân Loại">
            {candidate.industry || 'Chưa phân loại'}
          </Descriptions.Item>
          <Descriptions.Item label="Vị trí AI Phân Loại">
            {candidate.position || 'Chưa phân loại'}
          </Descriptions.Item>
          <Descriptions.Item label="Nội dung CV (Đã trích xuất)">
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
              {candidate.cvText || 'Không có dữ liệu CV'}
            </pre>
          </Descriptions.Item>
        </Descriptions>
      ) : (
        <p>Không tìm thấy dữ liệu ứng viên này.</p>
      )}
    </Card>
  );
}
