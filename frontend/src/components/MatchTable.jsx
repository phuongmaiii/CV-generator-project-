import React, { useState, useEffect, useContext } from 'react';
import { Table, Tag, Button, message } from 'antd';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

export default function MatchTable({ apiPath, columnsConfig, refreshKey }) {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const { user } = useContext(AuthContext);

    useEffect(() => {
        const fetchData = async () => {
            if (!apiPath) return;
            setLoading(true);
            try {
                const res = await api.get(apiPath);
                const list = res.data.content || res.data || [];
                // Luôn đảm bảo sắp xếp từ cao xuống thấp theo AI Score, kể cả khi backend đổi thứ tự
                const sorted = [...list].sort((a, b) => (Number(b.score) || 0) - (Number(a.score) || 0));
                setData(sorted);
            } catch (error) {
                console.error("Chi tiết lỗi API:", error.response?.data || error);
                message.error('Lỗi khi tải dữ liệu AI (kiểm tra lại quyền truy cập hoặc token).');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [apiPath, user, refreshKey]);

    // 1. Sắp xếp ứng viên/kết quả từ cao xuống thấp dựa theo điểm (matchScore hoặc score)
    const sortedData = [...data].sort((a, b) => {
        const scoreA = a.matchScore ?? a.score ?? 0;
        const scoreB = b.matchScore ?? b.score ?? 0;
        return scoreB - scoreA;
    });

    // 2. Cấu hình cột hiển thị mặc định
    const defaultColumns = [
        {
            title: 'Tên ứng viên / Vị trí',
            dataIndex: 'name',
            key: 'name',
            render: (text, record) => text || record.candidateName || record.jobTitle || 'N/A',
        },
        {
            title: 'Mức độ phù hợp (AI Score)',
            dataIndex: 'matchScore',
            key: 'matchScore',
            render: (val, record) => {
                const score = val ?? record.score ?? 0;
                return (
                    <Tag color={score >= 80 ? 'green' : score >= 50 ? 'orange' : 'red'}>
                        {score ? `${Number(score).toFixed(1)}%` : '0%'}
                    </Tag>
                );
            },
        },
        {
            title: 'Hành động',
            key: 'action',
            render: (_, record) => (
                <Button 
                    type="primary"
                    size="small"
                    onClick={() => {
                        const cvUrl = record.cvUrl || record.resumeUrl;
                        if (cvUrl) {
                            window.open(cvUrl, '_blank');
                        } else {
                            message.warning('Không tìm thấy đường dẫn CV của ứng viên!');
                        }
                    }}
                >
                    CV Preview
                </Button>
            ),
        },
    ];

    // 3. Hiển thị bảng dữ liệu
    return (
        <Table 
            dataSource={sortedData} 
            columns={columnsConfig || defaultColumns} 
            rowKey={(record) => record.id || record._id || record.matchId || Math.random()} 
            loading={loading} 
            pagination={{ pageSize: 5 }} 
        />
    );
}