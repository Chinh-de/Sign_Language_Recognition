import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import axiosInstance from "../axiosInstance";

import Sidebar from "../components/Sidebar";
import StreamResult from "../components/StreamResult";


const Recognition = () => {
    const [sessionId, setSessionId] = useState(null);
    const [result, setResult] = useState("");
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Lấy session ID từ localStorage nếu có
    useEffect(() => {
        const savedSessionId = localStorage.getItem('recognition_session_id');
        if (savedSessionId) {
            // Kiểm tra session còn tồn tại trên server không
            axiosInstance.get(`/recognition/status/${savedSessionId}/`)
                .then(response => {
                    if (response.data.status !== 'INACTIVE') {
                        setSessionId(savedSessionId);
                        setStatus(response.data.status);
                    } else {
                        // Xóa session ID không còn hợp lệ
                        localStorage.removeItem('recognition_session_id');
                    }
                })
                .catch(() => {
                    // Xóa session ID không còn hợp lệ
                    localStorage.removeItem('recognition_session_id');
                });
        }
    }, []);

    // Xử lý khi form được gửi
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        const camIP = e.target.ESP32CAM_IP.value;
        const deviceIP = e.target.device_IP.value || "";
        
        try {
            const response = await axiosInstance.post('/recognition/start/', {
                esp32cam_ip: camIP,
                esp32device_ip: deviceIP
            });
            
            // Lưu session ID
            const newSessionId = response.data.session_id;
            setSessionId(newSessionId);
            setStatus('ONLINE');
            
            // Lưu vào localStorage để duy trì giữa các phiên
            localStorage.setItem('recognition_session_id', newSessionId);
            
        } catch (error) {
            console.error("Lỗi khi bắt đầu phiên nhận diện:", error);
            alert(`Lỗi: ${error.response?.data?.error || "Không thể kết nối đến server"}`);
        } finally {
            setLoading(false);
        }
    };

    // Xử lý khi dừng phiên
    const handleStop = async () => {
        if (!sessionId) return;
        
        try {
            await axiosInstance.post('/recognition/stop/', {
                session_id: sessionId
            });
            
            setSessionId(null);
            setResult("");
            setStatus("");
            
            // Xóa khỏi localStorage
            localStorage.removeItem('recognition_session_id');
            
        } catch (error) {
            console.error("Lỗi khi dừng phiên:", error);
            alert("Không thể dừng phiên. Vui lòng thử lại.");
        }
    };

    // SSE để nhận kết quả và trạng thái
    useEffect(() => {
        if (!sessionId) return;
        
        const eventSource = new EventSource(`/recognition/result_sse/${sessionId}/`);
        
        eventSource.addEventListener('result', (event) => {
            const data = JSON.parse(event.data);
            setResult(data.result);
        });
        
        eventSource.addEventListener('status', (event) => {
            const data = JSON.parse(event.data);
            setStatus(data.status);
            
            // Nếu session không còn hoạt động
            if (data.status === 'INACTIVE') {
                eventSource.close();
                localStorage.removeItem('recognition_session_id');
                setSessionId(null);
            }
        });
        
        eventSource.onerror = (error) => {
            console.error("SSE error:", error);
            eventSource.close();
        };
        
        return () => {
            eventSource.close();
        };
    }, [sessionId]);

    // Ping định kỳ CHỈ khi session đang ONLINE
    useEffect(() => {
        // Chỉ ping khi session đang ONLINE
        if (!sessionId || status !== 'ONLINE') return;
        
        console.log("Bắt đầu ping định kỳ cho session ONLINE");
        
        const pingInterval = setInterval(async () => {
            try {
                // Kiểm tra trước khi ping để đảm bảo status vẫn là ONLINE
                if (status === 'ONLINE') {
                    const response = await axiosInstance.post('/recognition/ping/', {
                        session_id: sessionId
                    });
                    console.log("Ping thành công:", response.data);
                } else {
                    console.log("Bỏ qua ping vì status không còn là ONLINE:", status);
                }
            } catch (error) {
                console.error("Lỗi ping server:", error);
            }
        }, 10000); // Ping mỗi 10 giây
        
        return () => {
            console.log("Dừng ping định kỳ");
            clearInterval(pingInterval);
        };
    }, [sessionId, status]); // Thêm status vào dependencies để theo dõi thay đổi

    return (
        <div className="flex h-screen">
            <Sidebar 
                handleSubmit={handleSubmit} 
                handleStop={handleStop}
                loading={loading}
                sessionActive={!!sessionId}
                sessionStatus={status}
            />
            <div className="content flex-1 p-4 bg-gray-100">   
                <StreamResult 
                    sessionId={sessionId} 
                    result={result}
                    status={status} 
                />
            </div>
        </div>
    );
}

export default Recognition;