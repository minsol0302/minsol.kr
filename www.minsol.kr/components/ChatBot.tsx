'use client'

import { useState, useRef, useEffect } from 'react'
import { chatAPI, Message, DocumentSource } from '../utils/api'

// SVG 아이콘 컴포넌트
const SendIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
)

const LoaderIcon = () => (
  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
)

const BotIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
)

const UserIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
)

export default function ChatBot() {
  // 클라이언트에서만 초기 메시지 설정 (hydration 오류 방지)
  const [messages, setMessages] = useState<Message[]>([])
  const [isMounted, setIsMounted] = useState(false)
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null!)
  const inputRef = useRef<HTMLInputElement>(null)

  // 클라이언트 마운트 후 초기 메시지 설정
  useEffect(() => {
    setIsMounted(true)
    setMessages([
      {
        role: 'assistant',
        content: '안녕하세요! RAG 챗봇입니다. 무엇이 궁금하신가요?',
        timestamp: new Date().toISOString(),
      },
    ])
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    // 클라이언트에서만 실행
    if (typeof window !== 'undefined') {
      scrollToBottom()
    }
  }, [messages])

  // 컴포넌트 마운트 시 입력 필드에 자동 포커스
  useEffect(() => {
    // 클라이언트에서만 실행
    if (typeof window !== 'undefined') {
      inputRef.current?.focus()
    }
  }, [])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = input.trim()
    setInput('')
    setIsLoading(true)

    try {
      const response = await chatAPI.sendMessage(currentInput, 3)

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer || '응답을 생성할 수 없습니다.',
        timestamp: new Date().toISOString(),
        sources: Array.isArray(response.sources)
          ? response.sources.map((doc: any) => ({
            content: doc.content || '',
            metadata: doc.metadata || {},
          }))
          : [],
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Error sending message:', error)
      let errorContent = '죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.'

      if (error?.message?.includes('fetch') || error?.message?.includes('연결')) {
        errorContent = '서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.'
      } else if (error?.message?.includes('API URL')) {
        errorContent = 'API URL이 설정되지 않았습니다. 환경 변수를 확인해주세요.'
      } else if (error?.message) {
        errorContent = error.message
      }

      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      // 클라이언트에서만 포커스
      if (typeof window !== 'undefined') {
        setTimeout(() => {
          inputRef.current?.focus()
        }, 0)
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }


  // 클라이언트 마운트 전에는 빈 화면 (hydration 오류 방지)
  if (!isMounted) {
    return (
      <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="flex-1 flex items-center justify-center">
          <p className="text-gray-500">로딩 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-lg overflow-hidden">
      {/* 메시지 영역 */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-4 chat-messages"
        style={{
          paddingBottom: '100px' // 입력 영역 공간 확보
        }}
      >
        {messages.map((message, index) => (
          <div
            key={`message-${index}-${message.timestamp}`}
            className={`flex items-start gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                <BotIcon />
              </div>
            )}

            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-800'
                }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>

              {/* 소스 문서 표시 */}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300">
                  <p className="text-xs font-semibold mb-1">참조 문서:</p>
                  {message.sources.map((source, idx) => (
                    <div
                      key={`source-${idx}-${source.content?.substring(0, 20)}`}
                      className="text-xs bg-white bg-opacity-50 rounded p-2 mb-1"
                    >
                      <p className="line-clamp-2">{source.content || ''}</p>
                    </div>
                  ))}
                </div>
              )}

              {message.timestamp && isMounted && (
                <p className="text-xs mt-1 opacity-70" suppressHydrationWarning>
                  {new Date(message.timestamp).toLocaleTimeString('ko-KR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              )}
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                <UserIcon />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
              <BotIcon />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <LoaderIcon />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div
        className="border-t border-gray-200 p-4 bg-white chat-input-area shadow-lg flex-shrink-0"
      >
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            onKeyDown={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-text text-gray-900"
            disabled={isLoading}
            tabIndex={0}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <LoaderIcon />
            ) : (
              <SendIcon />
            )}
            <span>전송</span>
          </button>
        </div>
      </div>
    </div>
  )
}
