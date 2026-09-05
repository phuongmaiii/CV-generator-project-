import React, { useState, useContext, useEffect } from 'react';
import { Card, Form, Input, Button, message, DatePicker } from 'antd';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

export default function CreateJob() {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const currentUser = user || JSON.parse(localStorage.getItem('user'));
    if (currentUser && currentUser.companyName) {
      form.setFieldsValue({
        companyName: currentUser.companyName
      });
    }
  }, [user, form]);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const currentUser = user || JSON.parse(localStorage.getItem('user'));
      
      const payload = {
        ...values,
        deadline: values.deadline ? values.deadline.format('YYYY-MM-DD') : null,
        postedBy: currentUser?.id 
      };

      const res = await api.post('/jobs', payload);
      message.success('Đã đăng tin tuyển dụng thành công!');
      
      if (res.data && res.data.id) {
        navigate(`/hr-matches/${res.data.id}`);
      } else {
        navigate('/hr-dashboard');
      }
    } catch (error) {
      message.error('Có lỗi xảy ra khi tạo Job.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '10px' }}>
        <Button onClick={() => navigate('/hr-dashboard')} style={{ marginRight: '10px' }}>
          Quay lại Dashboard
        </Button>
        <Button onClick={logout} danger>Đăng xuất</Button>
      </div>

      <Card title="Tạo Mô Tả Công Việc Mới" style={{ maxWidth: 700, margin: '0 auto', borderRadius: '10px' }}>
        <Form form={form} layout="vertical" onFinish={onFinish}>
          
          {/* Hàng 1: Tiêu đề & Tên công ty */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <Form.Item 
              label="Tiêu đề công việc" 
              name="title" 
              rules={[{ required: true, message: 'Vui lòng nhập tiêu đề!' }]}
            >
              <Input placeholder="VD: Data Analyst Intern" />
            </Form.Item>

            <Form.Item 
              label="Tên công ty" 
              name="companyName" 
              rules={[{ required: true, message: 'Vui lòng nhập tên công ty!' }]}
            >
              <Input placeholder="VD: MoMo" />
            </Form.Item>
          </div>

          {/* Hàng 2: Địa điểm làm việc & Hạn chót */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
            <Form.Item 
              label="Địa điểm làm việc" 
              name="location" 
              rules={[{ required: true, message: 'Vui lòng nhập địa điểm làm việc!' }]}
            >
              <Input placeholder="VD: Quận 1, TP. Hồ Chí Minh" />
            </Form.Item>

            <Form.Item 
              label="Hạn chót nhận CV" 
              name="deadline" 
              rules={[{ required: true, message: 'Vui lòng chọn hạn chót!' }]}
            >
              <DatePicker style={{ width: '100%' }} placeholder="Chọn ngày" />
            </Form.Item>
          </div>

          {/* Hàng 3: Mô tả công việc */}
          <Form.Item 
            label="Mô tả công việc" 
            name="description" 
            rules={[{ required: true, message: 'Vui lòng nhập mô tả!' }]}
          >
            <Input.TextArea rows={4} placeholder="Nhập mô tả các đầu việc cần làm..." />
          </Form.Item>

          {/* Hàng 4: Yêu cầu kỹ năng */}
          <Form.Item 
            label="Yêu cầu kỹ năng" 
            name="requirements" 
            rules={[{ required: true, message: 'Vui lòng nhập yêu cầu!' }]}
          >
            <Input.TextArea rows={4} placeholder="VD: Python, SQL, IELTS 6.5+,..." />
          </Form.Item>

          {/* Nút submit */}
          <Button type="primary" htmlType="submit" loading={loading} block size="large">
            Lên Sóng Công Việc Này
          </Button>

        </Form>
      </Card>
    </div>
  );
}