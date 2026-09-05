import React from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import api from '../api'; // Đảm bảo file cấu hình axios của bạn nằm đúng ở đây

const { Title } = Typography;

export default function CreateJob() {
  const navigate = useNavigate();
  const [form] = Form.useForm();

  // Đây chính là đoạn code xử lý gửi dữ liệu lên Backend
  const onFinish = async (values) => {
    try {
      // Gọi API lưu Job
      const res = await api.post('/jobs', {
        title: values.title,
        companyName: values.companyName, 
        description: values.description,
        requirements: values.requirements,
        status: 'open' 
      });
      
      message.success('Đã đăng tin tuyển dụng thành công!');
      
      // Tự động chuyển sang trang xem ai phù hợp với Job này
      navigate(`/hr/matches/${res.data.id}`); 
      
    } catch (error) {
      console.error("Lỗi API:", error);
      message.error('Có lỗi xảy ra khi tạo Job.');
    }
  };

  return (
    <Card style={{ maxWidth: 800, margin: '40px auto' }}>
      <Title level={3}>Tạo Mô Tả Công Việc Mới</Title>
      
      <Form form={form} layout="vertical" onFinish={onFinish}>
        <Form.Item 
          label="Tiêu đề công việc" 
          name="title" 
          rules={[{ required: true, message: 'Vui lòng nhập tiêu đề!' }]}
        >
          <Input placeholder="Ví dụ: Data Analyst" />
        </Form.Item>

        {/* Ô nhập Tên công ty mới được thêm vào đây */}
        <Form.Item 
          label="Tên công ty" 
          name="companyName" 
          rules={[{ required: true, message: 'Vui lòng nhập tên công ty!' }]}
        >
          <Input placeholder="Ví dụ: Tech Corp, NAB, Bosch..." />
        </Form.Item>

        <Form.Item 
          label="Mô tả công việc" 
          name="description" 
          rules={[{ required: true, message: 'Vui lòng nhập mô tả!' }]}
        >
          <Input.TextArea rows={4} placeholder="Mô tả các công việc cần làm..." />
        </Form.Item>

        <Form.Item 
          label="Yêu cầu kỹ năng" 
          name="requirements" 
          rules={[{ required: true, message: 'Vui lòng nhập yêu cầu kỹ năng!' }]}
        >
          <Input.TextArea rows={4} placeholder="Yêu cầu kỹ năng (SQL, Python...)" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block size="large">
            Lên Sóng Công Việc Này
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
}