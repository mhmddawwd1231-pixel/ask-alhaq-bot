from flask import Flask, render_template_string, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from urllib.parse import quote

load_dotenv()
app = Flask(__name__)

# HTML Template مخصص
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اسأل الحق - بوت الأخبار الذكي</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            transition: background 0.3s ease;
        }
        
        /* Light Mode Colors */
        body.light-mode {
            background: #F4F4F5;
        }
        
        /* Dark Mode Colors */
        body.dark-mode {
            background: #27272A;
        }
        
        .chat-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            padding: 24px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 16px;
            transition: all 0.3s ease;
            background: #B90000;
            border: 1px solid #A00000;
        }
        
        .light-mode .header {
            background: #B90000;
            border: 1px solid #A00000;
        }
        
        .dark-mode .header {
            background: #B90000;
            border: 1px solid #A00000;
        }
        
        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .icon-container {
            background: white;
            padding: 12px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .logo-img {
            width: 70px;
            height: 70px;
            object-fit: contain;
        }
        
        .title {
            font-size: 32px;
            font-weight: bold;
            transition: color 0.3s ease;
            color: white;
        }
        
        .light-mode .title {
            color: white;
        }
        
        .dark-mode .title {
            color: white;
        }
        
        .subtitle {
            font-size: 14px;
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: color 0.3s ease;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .light-mode .subtitle {
            color: rgba(255, 255, 255, 0.9);
        }
        
        .dark-mode .subtitle {
            color: rgba(255, 255, 255, 0.9);
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: white;
            border-radius: 50%;
            animation: pulse 2s infinite;
            box-shadow: 0 0 10px white;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.9); }
        }
        
        .badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .theme-toggle {
            padding: 10px;
            border-radius: 12px;
            font-size: 20px;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .light-mode .theme-toggle {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .dark-mode .theme-toggle {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .theme-toggle:hover {
            transform: rotate(180deg) scale(1.1);
        }
        
        .new-chat-button {
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .light-mode .new-chat-button {
            background: white;
            color: #B90000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .dark-mode .new-chat-button {
            background: white;
            color: #B90000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .new-chat-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .messages-container {
            flex: 1;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }
        
        .light-mode .messages-container {
            background: white;
            border: 1px solid #E4E4E7;
        }
        
        .dark-mode .messages-container {
            background: #18181B;
            border: 1px solid #3F3F46;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }
        
        .messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .messages::-webkit-scrollbar-track {
            background: transparent;
            border-radius: 10px;
        }
        
        .light-mode .messages::-webkit-scrollbar-thumb {
            background: #E4E4E7;
            border-radius: 10px;
        }
        
        .dark-mode .messages::-webkit-scrollbar-thumb {
            background: #3F3F46;
            border-radius: 10px;
        }
        
        .message {
            margin-bottom: 16px;
            display: flex;
            gap: 12px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.assistant {
            justify-content: flex-start;
        }
        
        .message-icon {
            width: 40px;
            height: 40px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .light-mode .message.user .message-icon {
            background: #18181B;
            color: white;
            order: 1;
        }
        
        .dark-mode .message.user .message-icon {
            background: #FCFCFC;
            color: #18181B;
            order: 1;
        }
        
        .light-mode .message.assistant .message-icon {
            background: #F4F4F5;
            color: #18181B;
        }
        
        .dark-mode .message.assistant .message-icon {
            background: #3F3F46;
            color: #FCFCFC;
        }
        
        .message-content {
            max-width: 70%;
            padding: 16px 20px;
            border-radius: 16px;
            line-height: 1.8;
            font-size: 15px;
            position: relative;
            transition: all 0.3s ease;
        }
        
        .light-mode .message.user .message-content {
            background: #B90000;
            color: white;
            border-bottom-left-radius: 4px;
        }
        
        .dark-mode .message.user .message-content {
            background: #B90000;
            color: white;
            border-bottom-left-radius: 4px;
        }
        
        .light-mode .message.assistant .message-content {
            background: #F4F4F5;
            color: #18181B;
            border-bottom-right-radius: 4px;
            border: 1px solid #E4E4E7;
        }
        
        .dark-mode .message.assistant .message-content {
            background: #27272A;
            color: #FCFCFC;
            border-bottom-right-radius: 4px;
            border: 1px solid #3F3F46;
        }
        
        .search-info {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }
        
        .light-mode .search-info {
            background: #E4E4E7;
            color: #18181B;
            border: 1px solid #D4D4D8;
        }
        
        .dark-mode .search-info {
            background: #3F3F46;
            color: #A1A1AA;
            border: 1px solid #52525B;
        }
        
        .sources {
            margin-top: 12px;
            padding-top: 12px;
            transition: border-color 0.3s ease;
        }
        
        .light-mode .sources {
            border-top: 1px solid #E4E4E7;
        }
        
        .dark-mode .sources {
            border-top: 1px solid #3F3F46;
        }
        
        .source-title {
            font-size: 11px;
            margin-bottom: 6px;
            font-weight: bold;
            transition: color 0.3s ease;
        }
        
        .light-mode .source-title {
            color: #71717A;
        }
        
        .dark-mode .source-title {
            color: #A1A1AA;
        }
        
        .source-link {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 11px;
            margin: 4px 4px 4px 0;
            transition: all 0.3s;
        }
        
        .light-mode .source-link {
            background: #F4F4F5;
            border: 1px solid #E4E4E7;
            color: #18181B;
        }
        
        .dark-mode .source-link {
            background: #3F3F46;
            border: 1px solid #52525B;
            color: #A1A1AA;
        }
        
        .source-link:hover {
            transform: translateY(-2px);
        }
        
        .light-mode .source-link:hover {
            background: #E4E4E7;
            border-color: #18181B;
        }
        
        .dark-mode .source-link:hover {
            background: #52525B;
            border-color: #71717A;
        }
        
        .input-container {
            padding: 20px 24px;
            transition: all 0.3s ease;
        }
        
        .light-mode .input-container {
            border-top: 1px solid #E4E4E7;
            background: #FCFCFC;
        }
        
        .dark-mode .input-container {
            border-top: 1px solid #3F3F46;
            background: #18181B;
        }
        
        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        .input-field {
            flex: 1;
            padding: 16px 20px;
            border-radius: 16px;
            font-size: 15px;
            outline: none;
            transition: all 0.3s;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .light-mode .input-field {
            border: 1px solid #E4E4E7;
            background: #E4E4E7;
            color: #18181B;
        }
        
        .dark-mode .input-field {
            border: 1px solid #3F3F46;
            background: #3F3F46;
            color: #FCFCFC;
        }
        
        .light-mode .input-field::placeholder {
            color: #71717A;
        }
        
        .dark-mode .input-field::placeholder {
            color: #A1A1AA;
        }
        
        .input-field:focus {
            transform: scale(1.01);
        }
        
        .light-mode .input-field:focus {
            border-color: #18181B;
            box-shadow: 0 0 0 3px rgba(24, 24, 27, 0.1);
        }
        
        .dark-mode .input-field:focus {
            border-color: #71717A;
            box-shadow: 0 0 0 3px rgba(113, 113, 122, 0.2);
        }
        
        .send-button, .clear-button {
            padding: 16px 28px;
            border-radius: 16px;
            border: none;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 15px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .light-mode .send-button {
            background: #B90000;
            color: white;
            box-shadow: 0 4px 15px rgba(185, 0, 0, 0.4);
        }
        
        .dark-mode .send-button {
            background: #B90000;
            color: white;
            box-shadow: 0 4px 15px rgba(185, 0, 0, 0.4);
        }
        
        .send-button:hover:not(:disabled) {
            transform: translateY(-2px);
        }
        
        .light-mode .send-button:hover:not(:disabled) {
            box-shadow: 0 6px 20px rgba(185, 0, 0, 0.5);
            background: #A00000;
        }
        
        .dark-mode .send-button:hover:not(:disabled) {
            box-shadow: 0 6px 20px rgba(185, 0, 0, 0.5);
            background: #A00000;
        }
        
        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .light-mode .clear-button {
            background: white;
            color: #B90000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid #B90000;
        }
        
        .dark-mode .clear-button {
            background: white;
            color: #B90000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            border: 2px solid #B90000;
        }
        
        .clear-button:hover {
            transform: translateY(-2px);
            background: #FEE;
        }
        
        .loading {
            display: none;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            border-radius: 16px;
            margin-bottom: 16px;
            animation: slideIn 0.3s ease-out;
            transition: all 0.3s ease;
        }
        
        .light-mode .loading {
            background: #F4F4F5;
            border: 1px solid #E4E4E7;
        }
        
        .dark-mode .loading {
            background: #27272A;
            border: 1px solid #3F3F46;
        }
        
        .loading.show {
            display: flex;
        }
        
        .loading-text {
            font-size: 14px;
            transition: color 0.3s ease;
        }
        
        .light-mode .loading-text {
            color: #71717A;
        }
        
        .dark-mode .loading-text {
            color: #A1A1AA;
        }
        
        .loading-dots {
            display: flex;
            gap: 6px;
        }
        
        .loading-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }
        
        .light-mode .loading-dot {
            background: #18181B;
        }
        
        .dark-mode .loading-dot {
            background: #FCFCFC;
        }
        
        .loading-dot:nth-child(1) {
            animation-delay: -0.32s;
        }
        
        .loading-dot:nth-child(2) {
            animation-delay: -0.16s;
        }
        
        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1.2);
                opacity: 1;
            }
        }
        
        .welcome-message {
            text-align: center;
            padding: 20px 20px 40px 20px;
            transition: color 0.3s ease;
        }
        
        .welcome-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 8px;
            transition: color 0.3s ease;
        }
        
        .light-mode .welcome-title {
            color: #18181B;
        }
        
        .dark-mode .welcome-title {
            color: #FCFCFC;
        }
        
        .welcome-text {
            font-size: 16px;
            line-height: 1.8;
            transition: color 0.3s ease;
        }
        
        .light-mode .welcome-text {
            color: #71717A;
        }
        
        .dark-mode .welcome-text {
            color: #A1A1AA;
        }
        
        .quick-questions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
            margin-top: 24px;
            padding: 0 20px;
        }
        
        .quick-question {
            padding: 16px 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            font-size: 14px;
        }
        
        .light-mode .quick-question {
            background: white;
            border: 2px solid #B90000;
            color: #B90000;
            font-weight: 600;
        }
        
        .dark-mode .quick-question {
            background: #18181B;
            border: 2px solid #B90000;
            color: white;
            font-weight: 600;
        }
        
        .quick-question:hover {
            transform: translateY(-2px);
        }
        
        .light-mode .quick-question:hover {
            background: #B90000;
            color: white;
            box-shadow: 0 4px 15px rgba(185, 0, 0, 0.3);
        }
        
        .dark-mode .quick-question:hover {
            background: #B90000;
            color: white;
            box-shadow: 0 4px 15px rgba(185, 0, 0, 0.3);
        }
        
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 16px;
            }
            
            .message-content {
                max-width: 85%;
            }
            
            .quick-questions {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body class="light-mode">
    <div class="chat-container">
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <div class="icon-container">
                        <img src="/static/logo.jpeg" alt="اسأل الحق" class="logo-img">
                    </div>
                    <div>
                        <div class="title">اسأل الحق</div>
                        <div class="subtitle">
                            <span class="status-dot"></span>
                            <span>آخر الأخبار</span>
                        </div>
                    </div>
                </div>
                <div class="badges">
                    <button class="theme-toggle" onclick="toggleTheme()" title="تبديل الوضع">
                        <span id="themeIcon">🌙</span>
                    </button>
                    <button class="new-chat-button" onclick="clearChat()">
                        <span>➕</span>
                        <span>دردشة جديدة</span>
                    </button>
                </div>
            </div>
        </div>
        
        <div class="messages-container">
            <div class="messages" id="messages">
                <div class="welcome-message">
                    <div class="welcome-title">مرحباً بك في اسأل الحق</div>
                    <div class="welcome-text">
                        بوت ذكي <br>
                        يجيب أحدث الأخبار والمعلومات في ثوان<br>
                        بحث تلقائي | سرعة خيالية | تغطية عالمية
                    </div>
                </div>
                
                <div class="quick-questions">
                    <div class="quick-question" onclick="askQuestion('آخر الأخبار العالمية اليوم')">
                        آخر الأخبار العالمية اليوم
                    </div>
                    <div class="quick-question" onclick="askQuestion('أحوال الطقس في عمان اليوم')">
                        أحوال الطقس في عمان اليوم
                    </div>
                    <div class="quick-question" onclick="askQuestion('أحدث أخبار التكنولوجيا والذكاء الاصطناعي')">
                        أحدث أخبار التكنولوجيا
                    </div>
                    <div class="quick-question" onclick="askQuestion('أسعار العملات والأسهم الآن')">
                        أسعار العملات والأسهم
                    </div>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
                <span class="loading-text" id="loadingText">جاري البحث في الويب...</span>
            </div>
            
            <div class="input-container">
                <div class="input-wrapper">
                    <input 
                        type="text" 
                        id="messageInput" 
                        class="input-field" 
                        placeholder="اسأل عن أي شيء ..."
                        onkeypress="handleKeyPress(event)"
                    >
                    <button class="send-button" onclick="sendMessage()" id="sendButton">
                        إرسال
                    </button>
                    <button class="clear-button" onclick="clearChat()">
                        مسح
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load theme preference
        const savedTheme = localStorage.getItem('theme') || 'light-mode';
        document.body.className = savedTheme;
        updateThemeIcon();
        
        function toggleTheme() {
            const body = document.body;
            const currentTheme = body.classList.contains('light-mode') ? 'light-mode' : 'dark-mode';
            const newTheme = currentTheme === 'light-mode' ? 'dark-mode' : 'light-mode';
            
            body.classList.remove(currentTheme);
            body.classList.add(newTheme);
            
            localStorage.setItem('theme', newTheme);
            updateThemeIcon();
        }
        
        function updateThemeIcon() {
            const themeIcon = document.getElementById('themeIcon');
            const isDark = document.body.classList.contains('dark-mode');
            themeIcon.textContent = isDark ? '☀️' : '🌙';
        }
        
        function askQuestion(question) {
            document.getElementById('messageInput').value = question;
            sendMessage();
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        function clearChat() {
            const messages = document.getElementById('messages');
            messages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-title">مرحباً بك في اسأل الحق</div>
                    <div class="welcome-text">
                        بوت ذكي<br>
                        يجيب أحدث الأخبار والمعلومات في ثوان<br>
                        بحث تلقائي عبر الويب | سرعة خيالية | تغطية عالمية
                    </div>
                </div>
                
                <div class="quick-questions">
                    <div class="quick-question" onclick="askQuestion('آخر الأخبار العالمية اليوم')">
                        آخر الأخبار العالمية اليوم
                    </div>
                    <div class="quick-question" onclick="askQuestion('أحوال الطقس في عمان اليوم')">
                        أحوال الطقس في عمان اليوم
                    </div>
                    <div class="quick-question" onclick="askQuestion('أحدث أخبار التكنولوجيا والذكاء الاصطناعي')">
                        أحدث أخبار التكنولوجيا
                    </div>
                    <div class="quick-question" onclick="askQuestion('أسعار العملات والأسهم الآن')">
                        أسعار العملات والأسهم
                    </div>
                </div>
            `;
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            const welcome = document.querySelector('.welcome-message');
            const quickQuestions = document.querySelector('.quick-questions');
            if (welcome) welcome.style.display = 'none';
            if (quickQuestions) quickQuestions.style.display = 'none';
            
            addMessage(message, 'user');
            input.value = '';
            
            const loading = document.getElementById('loading');
            const loadingText = document.getElementById('loadingText');
            const sendButton = document.getElementById('sendButton');
            loading.classList.add('show');
            sendButton.disabled = true;
            
            const loadingMessages = [
                'جاري البحث في الويب...',
                'أبحث عن أحدث المعلومات...',
                'أتصفح الإنترنت...',
                'أجمع البيانات...'
            ];
            let msgIndex = 0;
            const loadingInterval = setInterval(() => {
                loadingText.textContent = loadingMessages[msgIndex];
                msgIndex = (msgIndex + 1) % loadingMessages.length;
            }, 1500);
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: message
                    }),
                });
                
                const data = await response.json();
                
                clearInterval(loadingInterval);
                
                if (data.success) {
                    addMessage(
                        data.response, 
                        'assistant', 
                        data.searched, 
                        data.sources
                    );
                } else {
                    addMessage('عذراً، حدث خطأ: ' + (data.error || 'غير معروف'), 'assistant');
                }
            } catch (error) {
                clearInterval(loadingInterval);
                addMessage('عذراً، حدث خطأ في الاتصال بالخادم', 'assistant');
            } finally {
                loading.classList.remove('show');
                sendButton.disabled = false;
                input.focus();
            }
        }
        
        function addMessage(text, type, searched = false, sources = null) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            
            let searchBadge = '';
            let sourcesHtml = '';
            
            if (type === 'assistant' && searched) {
                searchBadge = '<div class="search-info">🔍 تم البحث في الويب</div>';
                
                if (sources && sources.length > 0) {
                    sourcesHtml = '<div class="sources"><div class="source-title">المصادر:</div>';
                    sources.forEach(source => {
                        sourcesHtml += `<a href="${source.url}" target="_blank" class="source-link">
                            🔗 ${source.title}
                        </a>`;
                    });
                    sourcesHtml += '</div>';
                }
            }
            
            const iconText = type === 'user' ? '👤' : '🤖';
            
            messageDiv.innerHTML = `
                <div class="message-icon">${iconText}</div>
                <div class="message-content">
                    ${searchBadge}
                    ${text}
                    ${sourcesHtml}
                </div>
            `;
            
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('messageInput').focus();
        });
    </script>
</body>
</html>
'''

def search_web_advanced(query):
    """بحث متقدم باستخدام DuckDuckGo و SerpAPI"""
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            sources = []
            
            for result in soup.find_all('div', class_='result', limit=5):
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')
                
                if title_tag and snippet_tag:
                    title = title_tag.get_text(strip=True)
                    snippet = snippet_tag.get_text(strip=True)
                    url = title_tag.get('href', '')
                    
                    results.append(f"• **{title}**\n  {snippet}")
                    sources.append({
                        'title': title[:50] + '...' if len(title) > 50 else title,
                        'url': url
                    })
            
            if results:
                return '\n\n'.join(results), sources
        
        brave_url = "https://api.search.brave.com/res/v1/web/search"
        params = {
            'q': query,
            'count': 5
        }
        
        response = requests.get(brave_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            sources = []
            
            if 'web' in data and 'results' in data['web']:
                for item in data['web']['results'][:5]:
                    title = item.get('title', '')
                    description = item.get('description', '')
                    url = item.get('url', '')
                    
                    results.append(f"• **{title}**\n  {description}")
                    sources.append({
                        'title': title[:50] + '...' if len(title) > 50 else title,
                        'url': url
                    })
            
            if results:
                return '\n\n'.join(results), sources
        
        return None, []
        
    except Exception as e:
        print(f"خطأ في البحث: {str(e)}")
        return None, []

def call_groq_with_search(user_message):
    """استدعاء Groq مع البحث في الويب"""
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return None, 'مفتاح GROQ_API_KEY غير موجود', False, []
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"🔍 جاري البحث عن: {user_message}")
    search_results, sources = search_web_advanced(user_message)
    
    searched = bool(search_results)
    
    if search_results:
        system_prompt = f'''أنت اسأل الحق - بوت ذكي وسريع ومتصل بالإنترنت. التاريخ والوقت الحالي: {current_date}

📊 معلومات حديثة من البحث على الويب:
{search_results}

تعليمات مهمة:
1. استخدم المعلومات من البحث للإجابة بدقة
2. اذكر أحدث المعلومات والتواريخ إذا كانت متوفرة
3. كن واضحاً ومباشراً ومختصراً
4. أجب بالعربية الفصحى الواضحة
5. إذا كانت المعلومات غير كافية، قل ذلك بصراحة

تذكر: أنت متصل بالإنترنت وتعطي معلومات حديثة وموثوقة.'''
    else:
        system_prompt = f'''أنت اسأل الحق - بوت ذكي وسريع. التاريخ والوقت الحالي: {current_date}

تجيب على الأسئلة بالعربية بطريقة واضحة ومختصرة ومفيدة.'''
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"✅ تم الحصول على الرد {'مع البحث' if searched else 'بدون بحث'}")
            return answer, None, searched, sources
        else:
            return None, f'خطأ: {response.status_code}', False, []
    except Exception as e:
        return None, f'خطأ: {str(e)}', False, []

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'الرجاء إدخال سؤال'
            })
        
        print(f"💬 السؤال: {user_message}")
        
        response_text, error, searched, sources = call_groq_with_search(user_message)
        
        if response_text:
            return jsonify({
                'success': True,
                'response': response_text,
                'searched': searched,
                'sources': sources
            })
        else:
            return jsonify({
                'success': False,
                'error': error or 'حدث خطأ في الحصول على الرد'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'حدث خطأ: {str(e)}'
        })

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    groq_key = os.environ.get('GROQ_API_KEY', '')
    
    print("=" * 80)
    print("🎯 اسأل الحق - بوت الأخبار الذكي المتصل بالإنترنت!")
    print("=" * 80)
    print("📱 افتح المتصفح على: http://localhost:5000")
    print("-" * 80)
    
    if groq_key:
        print(f"✅ متصل بالإنترنت (Groq API)")
        print(f"🔑 المفتاح: {groq_key[:20]}...")
        print("🔍 البحث التلقائي: مُفعّل")
        print("⚡ السرعة: خيالية")
        print("♾️ الحدود: غير محدود تقريباً")
    else:
        print("❌ خطأ: مفتاح GROQ_API_KEY غير موجود")
        print("🔑 احصل على مفتاح من: https://console.groq.com/")
    
    print("=" * 80)
    print("✨ المميزات:")
    print("   🔍 بحث تلقائي في الويب لكل سؤال")
    print("   📰 آخر الأخبار والمعلومات الحديثة")
    print("   ⚡ سرعة استجابة خيالية")
    print("   🌍 تغطية عالمية شاملة")
    print("   💬 واجهة عربية جميلة ومتطورة")
    print("   🌙 وضع فاتح ووضع داكن")
    print("=" * 80)
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("📦 جاري تثبيت beautifulsoup4...")
        os.system('pip install beautifulsoup4 --quiet')
        print("✅ تم التثبيت!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
