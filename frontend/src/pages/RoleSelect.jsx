import { Card, Row, Col, Typography } from 'antd';
import { UserOutlined, TeamOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;

export default function RoleSelect() {
  const navigate = useNavigate();

  return (
    <div style={{ maxWidth: 700, margin: '80px auto', textAlign: 'center' }}>
      <Title level={2}>Bạn là ai?</Title>
      <Paragraph>Chọn vai trò để tiếp tục</Paragraph>
      <Row gutter={24} justify="center">
        <Col span={10}>
          <Card
            hoverable
            onClick={() => navigate('/login?role=candidate')}
            style={{ textAlign: 'center', padding: 24, cursor: 'pointer' }}
          >
            <UserOutlined style={{ fontSize: 48, color: '#1677ff' }} />
            <Title level={4} style={{ marginTop: 16 }}>Ứng viên</Title>
            <Paragraph>Upload CV và xem độ phù hợp với các vị trí đang tuyển</Paragraph>
          </Card>
        </Col>
        <Col span={10}>
          <Card
            hoverable
            onClick={() => navigate('/login?role=hr')}
            style={{ textAlign: 'center', padding: 24, cursor: 'pointer' }}
          >
            <TeamOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            <Title level={4} style={{ marginTop: 16 }}>Nhà tuyển dụng (HR)</Title>
            <Paragraph>Đăng tin tuyển dụng và xem danh sách ứng viên phù hợp</Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
}