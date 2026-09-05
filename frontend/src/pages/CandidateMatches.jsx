import React, { useState } from 'react';
import { Card, Button, Tag, message, Tooltip, Space } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftOutlined, ReloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import MatchTable from '../components/MatchTable';
import api from '../services/api';

export default function CandidateMatches() {
    const { candidateId } = useParams();
    const navigate = useNavigate();
    const [refreshing, setRefreshing] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    // Trước đây trang này tự cào lại TopCV mỗi lần mở, nên kết quả có thể đổi mỗi lần
    // xem. Giờ trang chỉ đọc kết quả đã lưu; nút này gọi endpoint /refresh để chủ động
    // cào lại khi người dùng thực sự muốn (vd. muốn xem cơ hội mới nhất).
    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            await api.post(`/match/candidate/${candidateId}/refresh`);
            setRefreshKey((k) => k + 1);
            message.success('Đã cập nhật danh sách vị trí phù hợp mới nhất.');
        } catch (error) {
            console.error('Lỗi khi làm mới:', error.response?.data || error);
            message.error('Không thể làm mới danh sách lúc này, vui lòng thử lại sau.');
        } finally {
            setRefreshing(false);
        }
    };

    const columnsConfig = [
        {
            title: 'Vị trí Tuyển dụng',
            key: 'jobTitle',
            render: (_, record) => (
                <Space direction="vertical" size={2}>
                    <strong style={{ color: '#1890ff', fontSize: '15px' }}>
                        {record.jobTitle || record.title || record.position || 'Chưa cập nhật tên vị trí'}
                    </strong>
                    {record.source === 'DEMO' && (
                        <Tooltip title="Không lấy được dữ liệu thật từ TopCV lúc tính điểm này — đây là dữ liệu minh hoạ, không phải tin tuyển dụng thật.">
                            <Tag icon={<InfoCircleOutlined />} color="default" style={{ width: 'fit-content' }}>
                                Dữ liệu minh hoạ
                            </Tag>
                        </Tooltip>
                    )}
                </Space>
            )
        },
        {
            title: 'Công ty',
            dataIndex: 'companyName',
            key: 'companyName',
            render: (val) => val || 'N/A',
        },
        {
            title: 'Mức độ phù hợp',
            key: 'score',
            render: (_, record) => {
                const finalScore = record.score || record.matchScore || record.aiScore || 0;
                let color = 'var(--color-match-low)';
                if (finalScore >= 80) color = 'var(--color-match-high)';
                else if (finalScore >= 50) color = 'var(--color-match-mid)';

                return (
                    <span className="score-figure" style={{ fontSize: 20, color }}>
                        {finalScore ? `${Number(finalScore).toFixed(0)}%` : '0%'}
                    </span>
                );
            }
        },
        {
            title: 'Hành động',
            key: 'action',
            render: (_, record) => {
                const targetJobId = record.jobId || record.jobPostingId || record.id;
                const externalUrl = record.jobUrl || record.url || record.link;

                return (
                    <Button
                        type="primary"
                        onClick={() => {
                            if (externalUrl) {
                                window.open(externalUrl, '_blank');
                            } else if (targetJobId) {
                                message.info(`Đang mở chi tiết Công việc ID: ${targetJobId}`);
                            } else {
                                message.error('Công việc lấy từ TopCV chưa được cấp Link hoặc ID!');
                            }
                        }}
                    >
                        Xem Công Việc
                    </Button>
                );
            }
        }
    ];

    return (
        <div style={{ padding: '30px', maxWidth: '1000px', margin: '0 auto', background: 'var(--color-paper)', minHeight: '100vh' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '24px', margin: 0 }}>
                    Vị trí phù hợp cho hồ sơ #{candidateId}
                </h2>
                <Space>
                    <Button icon={<ReloadOutlined />} loading={refreshing} onClick={handleRefresh}>
                        Làm mới
                    </Button>
                    <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/candidate-dashboard')}>
                        Về Dashboard
                    </Button>
                </Space>
            </div>

            <Card style={{ borderRadius: '10px', border: '1px solid var(--color-border)' }}>
                <MatchTable
                    apiPath={`/match/candidate/${candidateId}`}
                    columnsConfig={columnsConfig}
                    refreshKey={refreshKey}
                />
            </Card>
        </div>
    );
}
