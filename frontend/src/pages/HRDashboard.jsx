import React, { useState, useEffect, useContext } from 'react';
import { Card, Button, List, Tag, Spin, message, Empty, Typography, Popconfirm, Modal, Form, Input } from 'antd';
import { EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../services/api'; 
import { AuthContext } from '../context/AuthContext';

const { Title, Text } = Typography;

export default function HRDashboard() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingJob, setEditingJob] = useState(null);
    const [form] = Form.useForm();
    
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);

   const fetchMyJobs = async () => {
        try {
            setLoading(true);
            // SỬA DÒNG NÀY: Gọi API mới lấy theo company
            const res = await api.get(`/jobs/hr/my-company-jobs`);
            
            const jobData = res.data.content || res.data || [];
            setJobs(jobData);
        } catch (error) {
            const status = error.response?.status;
            if (status === 401 || status === 403) {
                message.error("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
                navigate('/');
            } else {
                message.error("Không thể tải danh sách công việc.");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMyJobs();
    }, [navigate]);

    const handleDelete = async (id) => {
        try {
            // Cần truyền token nếu api.js chưa cấu hình tự gắn header
            await api.delete(`/jobs/${id}`);
            message.success("Đã xóa công việc!");
            fetchMyJobs(); 
        } catch (error) {
            message.error(error.response?.data || "Lỗi khi xóa công việc!");
        }
    };

    const openEditModal = (job) => {
        setEditingJob(job);
        form.setFieldsValue({
            title: job.title || job.jobTitle,
            location: job.location,
            description: job.description,
            requirements: job.requirements
        });
        setIsModalOpen(true);
    };

    const handleUpdate = async (values) => {
        try {
            const jobId = editingJob.id || editingJob.jobPostingId || editingJob._id;
            await api.put(`/jobs/${jobId}`, values);
            message.success("Đã cập nhật thành công!");
            setIsModalOpen(false);
            fetchMyJobs();
        } catch (error) {
            message.error(error.response?.data || "Lỗi cập nhật!");
        }
    };

    const storedUser = JSON.parse(localStorage.getItem('user'));
    const companyName = user?.companyName || storedUser?.companyName || "Công ty chưa cập nhật";

    return (
        <div style={{ padding: '30px', maxWidth: '1000px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <Title level={2} style={{ margin: 0 }}>
                    Quản lý Tuyển dụng - <Text type="secondary">{companyName}</Text>
                </Title>
                
                <div>
                    <Button type="primary" onClick={() => navigate('/create-job')} style={{ marginRight: '10px' }}>
                        Thêm vị trí muốn tuyển
                    </Button>
                    {/* ĐÃ XÓA BỎ NÚT NẠP JOB MẪU TẠI ĐÂY */}
                    <Button danger onClick={() => {
                        localStorage.clear();
                        navigate('/');
                    }}>
                        Đăng xuất
                    </Button>
                </div>
            </div>

            <Card>
                {loading ? (
                    <div style={{ textAlign: 'center', padding: '50px' }}>
                        <Spin size="large" description="Đang tải danh sách công việc..." />
                    </div>
                ) : jobs.length === 0 ? (
                    <Empty description="Bạn chưa đăng vị trí tuyển dụng nào." />
                ) : (
                    <List
                        itemLayout="horizontal"
                        dataSource={jobs}
                        renderItem={(job) => {
                            const jobId = job.id || job.jobPostingId || job._id;
                            const isExpired = job.status === 'EXPIRED';

                            return (
                                <List.Item
                                    style={{ 
                                        borderBottom: '1px solid #f0f0f0', 
                                        padding: '20px 15px', 
                                        background: isExpired ? '#fafafa' : '#fff', 
                                        cursor: 'pointer' 
                                    }}
                                    onClick={() => navigate(`/hr-matches/${jobId}`)}
                                    actions={[
                                        <Button 
                                            key="view" type="primary" ghost icon={<EyeOutlined />} 
                                            onClick={(e) => { e.stopPropagation(); navigate(`/hr-matches/${jobId}`); }}
                                        >
                                            Xem Ứng viên
                                        </Button>,
                                        <Button 
                                            key="edit" icon={<EditOutlined />} 
                                            onClick={(e) => { e.stopPropagation(); openEditModal(job); }}
                                        >
                                            Sửa
                                        </Button>,
                                        <Popconfirm 
                                            key="delete" title="Xóa vị trí này?" 
                                            description="Thao tác này không thể hoàn tác." 
                                            onConfirm={(e) => { e.stopPropagation(); handleDelete(jobId); }} 
                                            okText="Xóa" cancelText="Hủy"
                                        >
                                            <Button danger icon={<DeleteOutlined />} onClick={(e) => e.stopPropagation()}>Xóa</Button>
                                        </Popconfirm>
                                    ]}
                                >
                                    <List.Item.Meta
                                        title={<Text strong style={{ fontSize: '16px' }}>{job.title || job.jobTitle || 'Vị trí chưa đặt tên'}</Text>}
                                        description={
                                            <div style={{ marginTop: '8px' }}>
                                               <span>Địa điểm: {job.location && job.location !== 'N/A' ? job.location : 'Hồ Chí Minh / Hà Nội'}</span>
                                                <Tag color={isExpired ? "default" : "blue"} style={{ marginLeft: '10px' }}>
                                                    {job.status || 'Đang tuyển'}
                                                </Tag>
                                            </div>
                                        }
                                    />
                                </List.Item>
                            );
                        }}
                    />
                )}
            </Card>

            <Modal
                title="Chỉnh sửa công việc"
                open={isModalOpen}
                onCancel={() => setIsModalOpen(false)}
                footer={null}
            >
                <Form form={form} layout="vertical" onFinish={handleUpdate}>
                    <Form.Item name="title" label="Tiêu đề công việc" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item 
    label="Địa điểm làm việc" 
    name="location" 
    rules={[{ required: true, message: 'Vui lòng nhập địa điểm làm việc!' }]}
>
    <Input placeholder="VD: Quận 1, TP. Hồ Chí Minh" />
</Form.Item>
                    <Form.Item name="description" label="Mô tả công việc">
                        <Input.TextArea rows={4} />
                    </Form.Item>
                    <Form.Item name="requirements" label="Yêu cầu">
                        <Input.TextArea rows={4} />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" block>Cập nhật</Button>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
}