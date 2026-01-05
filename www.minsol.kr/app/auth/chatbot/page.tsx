'use client'

import { useEffect, useState } from 'react'
import ChatBot from '../../../components/ChatBot'
import { useRouter } from 'next/navigation'

export default function ChatbotPage() {
  const [isMounted, setIsMounted] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setIsMounted(true)
  }, [])

  const handleBack = () => {
    router.back()
  }

  if (!isMounted) {
    return null
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-4xl">
        <div className="mb-4">
          <button
            onClick={handleBack}
            className="text-gray-600 hover:text-gray-900 flex items-center gap-2 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            뒤로 가기
          </button>
        </div>
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            RAG 챗봇
          </h1>
          <p className="text-gray-600">
            LangChain과 pgvector를 사용한 지식 기반 챗봇
          </p>
        </div>
        <ChatBot />
      </div>
    </main>
  )
}
