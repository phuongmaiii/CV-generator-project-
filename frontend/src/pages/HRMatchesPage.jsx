import React from 'react';
import { Card, Button } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftOutlined } from '@ant-design/icons';
import MatchTable from '../components/MatchTable';

export default function HRMatchesPage() {
    const { jobPostingId } = useParams();
    const navigate = useNavigate();

    // Cấu hình chính xác các cột khớp với DTO trả về từ API /match/job/{id}/ranked
    const columnsConfig = [
        {
            title: 'Tên ứng viên',
            dataIndex: 'candidateName',
            key: 'candidateName',
            render: (text, record) => text || record.fullName || record.name || 'Ứng viên',
        },
        {
            title: 'Email liên hệ',
            dataIndex: 'email',
            key: 'email',
            render: (text, record) => {
                const email = text || record.candidateEmail;
                // Phòng trường hợp dữ liệu cũ còn lẫn message lỗi AI thay vì email thật
                if (!email || email.startsWith('LỖI AI:')) return 'Chưa cập nhật';
                return email;
            },
        },
        {
            title: 'Độ phù hợp (AI Score)',
            dataIndex: 'score',
            key: 'score',
            render: (score) => `${score !== undefined && score !== null ? score : 0}%`,
        },
        {
            title: 'Hành động',
            key: 'action',
            render: (_, record) => (
                <Button 
                    type="primary" 
                    ghost 
                    onClick={() => navigate(`/candidate-details/${record.candidateId || record.id}?jobPostingId=${jobPostingId}`)}
                >
                    Preview CV
                </Button>
            ),
        },
    ];

    return (
        <div style={{ padding: '30px', maxWidth: '1000px', margin: '0 auto', background: '#f0f2f5', minHeight: '100vh' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Danh Sách Ứng Viên Phù Hợp</h2>
                <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/hr-dashboard')}>
                    Quay lại Dashboard
                </Button>
            </div>

            <Card style={{ borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                <MatchTable
                    apiPath={`/match/job/${jobPostingId}/ranked`} 
                    columnsConfig={columnsConfig}
                />
            </Card>
        </div>
    );
}
