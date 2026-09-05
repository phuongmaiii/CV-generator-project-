import { useState, useContext, useEffect } from 'react';
import { Upload, Button, Form, Input, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';

// Form upload CV dùng chung cho trang /upload-cv và cho Modal "Ứng tuyển vị trí khác"
// trên Dashboard, để không lặp lại logic gọi API ở 2 nơi.
export default function UploadCvForm({ onSuccess }) {
  const [fileList, setFileList] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user } = useContext(AuthContext);
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        fullName: user.fullName || user.name || '',
        email: user.email || ''
      });
    }
  }, [user, form]);

  const onFinish = async (values) => {
    if (fileList.length === 0) {
      message.error('Vui lòng chọn file CV');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileList[0]);
    formData.append('fullName', values.fullName);
    formData.append('email', values.email);

    setLoading(true);
    try {
      const res = await api.post('/candidates/upload-cv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      message.success('Đã tải CV thành công và tìm thấy vị trí phù hợp!');
      setFileList([]);

      if (res.data && res.data.id) {
        onSuccess?.(res.data.id);
      } else {
        message.warning('Upload thành công nhưng không nhận được ID ứng viên từ Backend.');
      }
    } catch (err) {
      console.error('Lỗi upload:', err);
      message.error(err.response?.data?.error || err.response?.data?.message || 'Có lỗi xảy ra khi upload CV');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item
        label="Họ tên"
        name="fullName"
        rules={[{ required: true, message: 'Vui lòng nhập họ tên!' }]}
      >
        <Input disabled style={{ color: '#000', backgroundColor: '#f5f5f5' }} />
      </Form.Item>

      <Form.Item
        label="Email"
        name="email"
        rules={[{ required: true, type: 'email', message: 'Vui lòng nhập email!' }]}
      >
        <Input disabled style={{ color: '#000', backgroundColor: '#f5f5f5' }} />
      </Form.Item>

      <Form.Item label="File CV (PDF)">
        <Upload
          beforeUpload={(file) => {
            setFileList([file]);
            return false;
          }}
          maxCount={1}
          accept=".pdf"
          fileList={fileList}
          onRemove={() => setFileList([])}
        >
          <Button icon={<UploadOutlined />}>Chọn file</Button>
        </Upload>
      </Form.Item>

      <Button type="primary" htmlType="submit" loading={loading} block>
        Tải lên
      </Button>
    </Form>
  );
}
