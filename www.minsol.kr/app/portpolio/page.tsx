'use client';

import { useState, useRef, useEffect } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';

interface FileInfo {
    file: File;
    id: string;
    name: string;
    size: number;
    type: string;
    preview?: string;
}

export default function PortfolioUpload() {
    const router = useRouter();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [files, setFiles] = useState<FileInfo[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [alert, setAlert] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'application/pdf', 'text/plain'];

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    };

    const showAlert = (message: string, type: 'success' | 'error' = 'success') => {
        setAlert({ message, type });
        setTimeout(() => setAlert(null), 3000);
    };

    const validateFile = (file: File): string | null => {
        if (!ALLOWED_TYPES.includes(file.type)) {
            return `지원하지 않는 파일 형식입니다: ${file.name}`;
        }
        if (file.size > MAX_FILE_SIZE) {
            return `파일 크기가 너무 큽니다 (최대 10MB): ${file.name}`;
        }
        return null;
    };

    const addFiles = (newFiles: FileList | File[]) => {
        const fileArray = Array.from(newFiles);
        const validFiles: FileInfo[] = [];
        const errors: string[] = [];

        fileArray.forEach((file) => {
            const error = validateFile(file);
            if (error) {
                errors.push(error);
            } else {
                const isImage = file.type.startsWith('image/');
                const preview = isImage ? URL.createObjectURL(file) : undefined;

                validFiles.push({
                    file,
                    id: Math.random().toString(36).substring(7),
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    preview,
                });
            }
        });

        if (errors.length > 0) {
            errors.forEach((error) => showAlert(error, 'error'));
        }

        if (validFiles.length > 0) {
            setFiles((prev: FileInfo[]) => [...prev, ...validFiles]);
            validFiles.forEach((fileInfo) => {
                showAlert(
                    `파일 추가됨: ${fileInfo.name} (${formatFileSize(fileInfo.size)})`,
                    'success'
                );
            });
        }
    };

    const handleDeleteFile = (id: string) => {
        setFiles((prev: FileInfo[]) => {
            const fileToDelete = prev.find(f => f.id === id);
            if (fileToDelete?.preview) {
                URL.revokeObjectURL(fileToDelete.preview);
            }
            return prev.filter(f => f.id !== id);
        });
        showAlert('파일이 삭제되었습니다.', 'success');
    };

    const getFileIcon = (type: string) => {
        if (type === 'application/pdf') {
            return (
                <svg className="w-12 h-12 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
            );
        }
        if (type === 'text/plain') {
            return (
                <svg className="w-12 h-12 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
            );
        }
        return (
            <svg className="w-12 h-12 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
        );
    };

    const handleDragEnter = (e: DragEvent<HTMLDivElement>): void => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: DragEvent<HTMLDivElement>): void => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e: DragEvent<HTMLDivElement>): void => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e: DragEvent<HTMLDivElement>): void => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            addFiles(e.dataTransfer.files);
        }
    };

    const handleFileSelect = (e: ChangeEvent<HTMLInputElement>): void => {
        if (e.target.files && e.target.files.length > 0) {
            addFiles(e.target.files);
        }
    };

    const handleDeleteAll = () => {
        setFiles([]);
        showAlert('모든 파일이 삭제되었습니다.', 'success');
    };

    const handleAddToPortfolio = async () => {
        if (files.length === 0) {
            showAlert('추가할 파일이 없습니다.', 'error');
            return;
        }

        try {
            // FormData 생성
            const formData = new FormData();
            files.forEach((fileInfo) => {
                formData.append('files', fileInfo.file);
            });

            // FastAPI 서버로 직접 업로드
            const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
            const response = await fetch(`${apiBase}/api/upload`, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showAlert(
                    `${data.files.length}개의 파일이 포트폴리오에 저장되었습니다.`,
                    'success'
                );
                // 저장 성공 후 파일 목록 초기화 (선택사항)
                // setFiles([]);
            } else {
                const errorMessage = data.detail?.message || data.message || '파일 저장에 실패했습니다.';
                showAlert(errorMessage, 'error');
            }
        } catch (error) {
            console.error('파일 업로드 오류:', error);
            showAlert('파일 저장 중 오류가 발생했습니다. FastAPI 서버가 실행 중인지 확인해주세요.', 'error');
        }
    };

    const handleBack = () => {
        router.back();
    };

    // 컴포넌트 언마운트 시 메모리 정리
    useEffect(() => {
        return () => {
            files.forEach((fileInfo) => {
                if (fileInfo.preview) {
                    URL.revokeObjectURL(fileInfo.preview);
                }
            });
        };
    }, []);

    return (
        <div className="flex min-h-screen items-center justify-center bg-blue-50 font-sans">
            <div className="w-full max-w-2xl px-6 py-8">
                {/* 제목 */}
                <h1 className="text-4xl font-bold text-center text-black mb-6">
                    포트폴리오 업로드
                </h1>

                {/* 안내 문구 */}
                <p className="text-center text-black mb-6">
                    드래그 앤 드롭으로 파일을 업로드하거나 클릭하여 파일을 선택하세요
                </p>

                {/* 드래그 앤 드롭 영역 */}
                <div
                    className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${isDragging
                        ? 'border-blue-500 bg-blue-100'
                        : 'border-gray-300 bg-white'
                        }`}
                    onDragEnter={handleDragEnter}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                >
                    {/* 폴더 아이콘 */}
                    <div className="flex justify-center mb-4">
                        <svg
                            className="w-24 h-24 text-yellow-500"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                        >
                            <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                        </svg>
                    </div>

                    <p className="text-black mb-2 text-lg">파일을 여기에 드래그하세요</p>
                    <p className="text-black mb-4 text-sm">또는 클릭하여 파일을 선택하세요</p>

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-6 rounded-lg transition-colors mb-4"
                    >
                        파일 선택
                    </button>

                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.txt"
                        onChange={handleFileSelect}
                        className="hidden"
                    />

                    <p className="text-sm text-gray-600 mt-4">
                        지원 형식: JPG, PNG, GIF, WebP, PDF, TXT (최대 10MB)
                    </p>
                </div>

                {/* 액션 버튼 */}
                <div className="flex gap-4 mt-6">
                    <button
                        onClick={handleDeleteAll}
                        className="flex-1 bg-gray-200 hover:bg-gray-300 text-black font-medium py-3 px-6 rounded-lg transition-colors"
                    >
                        모든 파일 삭제
                    </button>
                    <button
                        onClick={handleAddToPortfolio}
                        className="flex-1 bg-green-500 hover:bg-green-600 text-white font-medium py-3 px-6 rounded-lg transition-colors"
                    >
                        포트폴리오에 추가 ({files.length})
                    </button>
                </div>

                {/* 파일 미리보기 목록 */}
                {files.length > 0 && (
                    <div className="mt-6">
                        <h2 className="text-xl font-semibold text-black mb-4">업로드된 파일 ({files.length})</h2>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                            {files.map((fileInfo) => (
                                <div
                                    key={fileInfo.id}
                                    className="relative group border border-gray-300 rounded-lg overflow-hidden bg-white hover:shadow-lg transition-shadow"
                                >
                                    {/* 이미지 미리보기 또는 아이콘 */}
                                    <div className="aspect-square flex items-center justify-center bg-gray-100">
                                        {fileInfo.preview ? (
                                            <img
                                                src={fileInfo.preview}
                                                alt={fileInfo.name}
                                                className="w-full h-full object-cover"
                                            />
                                        ) : (
                                            <div className="flex flex-col items-center justify-center p-2">
                                                {getFileIcon(fileInfo.type)}
                                            </div>
                                        )}
                                    </div>

                                    {/* 파일 정보 */}
                                    <div className="p-2">
                                        <p className="text-xs text-gray-700 truncate" title={fileInfo.name}>
                                            {fileInfo.name}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {formatFileSize(fileInfo.size)}
                                        </p>
                                    </div>

                                    {/* 삭제 버튼 */}
                                    <button
                                        onClick={() => handleDeleteFile(fileInfo.id)}
                                        className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                        title="파일 삭제"
                                    >
                                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                            <path
                                                fillRule="evenodd"
                                                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* 이전 페이지로 버튼 */}
                <button
                    onClick={handleBack}
                    className="w-full mt-4 bg-white hover:bg-gray-50 border border-gray-300 text-black font-medium py-3 px-6 rounded-lg transition-colors"
                >
                    ← 이전 페이지로
                </button>

                {/* 알림 */}
                {alert && (
                    <div
                        className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 animate-slide-in ${alert.type === 'success'
                            ? 'bg-green-500 text-white'
                            : 'bg-red-500 text-white'
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            {alert.type === 'success' ? (
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path
                                        fillRule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                            ) : (
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path
                                        fillRule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                            )}
                            <span>{alert.message}</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

