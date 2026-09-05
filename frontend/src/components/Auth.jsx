import React, { useState, useContext } from 'react';
import { Form, Input, Button, Tabs, message, Radio, Typography, Select } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, IdcardOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

const TOP_COMPANIES = [
    "FPT Software", "Viettel Group", "MoMo", "VNG Corporation",
    "Shopee Vietnam", "Tiki", "VNPT", "Techcombank", "MB Bank", 
    "VPBank", "KMS Technology", "NashTech", "Axon", "Gojek", 
    "Grab", "OneMount Group", "Vingroup", "ZaloPay", "Sendo", "Be Group"
];

export default function Auth() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialRole = queryParams.get('role') || 'candidate';
  
  const [selectedRole, setSelectedRole] = useState(initialRole);
  const [formInstance] = Form.useForm();

  const onFinish = async (values, isLogin) => {
    setLoading(true);
    try {
      // Xác định đúng endpoint dựa vào hành động (đăng nhập hay đăng ký)
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      
      const payload = isLogin 
        ? { email: values.email, password: values.password }
        : { 
            email: values.email, 
            password: values.password, 
            fullName: values.fullName, 
            role: values.role.toUpperCase(),
            companyName: values.companyName || null
          };

      // Đã sửa lại thành endpoint và payload
      const res = await api.post(endpoint, payload);
      
      if (isLogin) {
        login({ ...res.data, token: res.data.token });
        message.success('Đăng nhập thành công!');
        navigate(res.data.role?.toLowerCase() === 'hr' ? '/hr-dashboard' : '/candidate-dashboard');
      } else {
        message.success('Đăng ký thành công! Vui lòng chuyển sang tab Đăng nhập.');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error 
                  || error.response?.data?.message 
                  || 'Thông tin không hợp lệ hoặc email đã tồn tại!';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const loginForm = (
    <Form name="login" onFinish={(vals) => onFinish(vals, true)} layout="vertical">
      <Form.Item name="email" rules={[{ required: true, message: 'Vui lòng nhập Email!' }]}>
        <Input prefix={<UserOutlined />} placeholder="Email" size="large" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true, message: 'Vui lòng nhập Mật khẩu!' }]}>
        <Input.Password prefix={<LockOutlined />} placeholder="Mật khẩu" size="large" />
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={loading} block size="large">
        Đăng nhập
      </Button>
    </Form>
  );

  const registerForm = (
    <Form 
        form={formInstance} 
        name="register" 
        onFinish={(vals) => onFinish(vals, false)} 
        layout="vertical" 
        initialValues={{ role: initialRole }}
        onValuesChange={(changedValues) => {
            if (changedValues.role) {
                setSelectedRole(changedValues.role.toLowerCase());
            }
        }}
    >
      <Form.Item name="fullName" rules={[{ required: true, message: 'Vui lòng nhập Họ tên!' }]}>
        <Input prefix={<IdcardOutlined />} placeholder="Họ và tên" size="large" />
      </Form.Item>
      <Form.Item name="email" rules={[{ required: true, type: 'email', message: 'Email không hợp lệ!' }]}>
        <Input prefix={<MailOutlined />} placeholder="Email" size="large" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true, message: 'Vui lòng nhập Mật khẩu!' }]}>
        <Input.Password prefix={<LockOutlined />} placeholder="Mật khẩu" size="large" />
      </Form.Item>
      <Form.Item name="role" label="Bạn là:">
        <Radio.Group>
          <Radio value="candidate">Ứng viên</Radio>
          <Radio value="hr">Nhà tuyển dụng</Radio>
        </Radio.Group>
      </Form.Item>
      
      {selectedRole === 'hr' && (
        <Form.Item 
            name="companyName" 
            label="Chọn công ty của bạn" 
            rules={[{ required: true, message: 'Vui lòng chọn công ty!' }]}
        >
            <Select
                showSearch
                placeholder="Gõ hoặc chọn tên công ty..."
                options={TOP_COMPANIES.map(company => ({
                    value: company,
                    label: company
                }))}
                filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
            />
        </Form.Item>
      )}

      <Button type="primary" htmlType="submit" loading={loading} block size="large">
        Đăng ký
      </Button>
    </Form>
  );

  const items = [
    { key: '1', label: 'Đăng nhập', children: loginForm },
    { key: '2', label: 'Đăng ký', children: registerForm },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--color-paper)' }}>
      <div
        className="auth-hero-panel"
        style={{
          flex: '1 1 45%',
          background: 'linear-gradient(160deg, #23433A 0%, #172E27 100%)',
          color: '#F3F4EF',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '64px 56px',
        }}
      >
        <div style={{ maxWidth: 380 }}>
          <h1 style={{ fontSize: 40, lineHeight: 1.15, color: '#F3F4EF', marginBottom: 20 }}>
            Đúng người, đúng vị trí, đúng lúc.
          </h1>
          <p style={{ fontSize: 16, lineHeight: 1.6, color: 'rgba(243,244,239,0.8)', margin: 0 }}>
            Tải CV lên một lần, xem ngay mức độ phù hợp với từng vị trí đang tuyển —
            hoặc tìm đúng ứng viên cho tin tuyển dụng của bạn.
          </p>
        </div>
      </div>

      <div style={{ flex: '1 1 55%', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ width: '100%', maxWidth: 380 }}>
          <h2 style={{ fontSize: 24, marginBottom: 4 }}>Hệ thống CV AI</h2>
          <p style={{ color: 'var(--color-ink-muted)', marginBottom: 24, fontSize: 14 }}>
            Đăng nhập hoặc tạo tài khoản để bắt đầu.
          </p>
          <Tabs defaultActiveKey="1" items={items} />
        </div>
      </div>
    </div>
  );
}