<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fast Food Crew</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Custom Scrollbar styling for sleek dark look */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #090d16;
        }
        ::-webkit-scrollbar-thumb {
            background: #1f293d;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #374151;
        }

        /* Message Bubble Animations */
        @keyframes bubblePop {
            0% {
                opacity: 0;
                transform: translateY(12px) scale(0.96);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .animate-bubble {
            animation: bubblePop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }

        /* Typing Dots Animation */
        @keyframes typingDot {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.4;
            }
            30% {
                transform: translateY(-5px);
                opacity: 1;
            }
        }

        .dot-1 { animation: typingDot 1.4s infinite 0s; }
        .dot-2 { animation: typingDot 1.4s infinite 0.2s; }
        .dot-3 { animation: typingDot 1.4s infinite 0.4s; }

        /* Smooth glow for interactive elements */
        .btn-send:hover {
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
        }
    </style>
</head>
<body class="bg-gray-950 font-sans antialiased text-gray-100 flex items-center justify-center min-h-screen p-0 sm:p-4">

    <!-- Mobile Device Outer Container -->
    <div class="w-full sm:max-w-md h-screen sm:h-[840px] bg-slate-900 sm:rounded-[36px] shadow-2xl flex flex-col overflow-hidden border border-slate-800 relative">
        
        <!-- TOP STATUS BAR -->
        <div class="bg-slate-950/90 backdrop-blur-md text-white px-6 pt-3 pb-2 flex justify-between items-center text-xs font-semibold z-20 border-b border-slate-800/60 select-none">
            <!-- Current Time Display -->
            <div id="live-clock" class="tracking-wider text-sm font-medium text-slate-200">
                12:00 PM
            </div>

            <!-- Speaker/Notch Graphic for aesthetic -->
            <div class="w-20 h-4 bg-black rounded-full hidden sm:block border border-slate-800/80"></div>

            <!-- Signal / Wifi / Battery Icons -->
            <div class="flex items-center space-x-2 text-slate-300">
                <i class="fa-solid fa-signal text-[11px]"></i>
                <i class="fa-solid fa-wifi text-[11px]"></i>
                <i class="fa-solid fa-battery-full text-sm text-emerald-400"></i>
            </div>
        </div>

        <!-- CHAT HEADER -->
        <div class="bg-slate-900/95 backdrop-blur-md border-b border-slate-800 px-4 py-3 flex items-center justify-between z-10 shadow-md">
            <div class="flex items-center space-x-3">
                <button class="text-slate-400 hover:text-white transition p-1 rounded-full focus:outline-none">
                    <i class="fa-solid fa-chevron-left text-lg"></i>
                </button>
                
                <!-- Group Avatar & Info -->
                <div class="relative flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-tr from-amber-600 to-yellow-500 text-white font-bold shadow-md">
                    <i class="fa-solid fa-hard-hat text-lg"></i>
                    <span class="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full"></span>
                </div>

                <div>
                    <h1 class="font-bold text-sm text-slate-100 leading-snug flex items-center gap-1.5">
                        Fast Food Crew
                        <span class="bg-amber-500/20 text-amber-400 text-[10px] px-1.5 py-0.5 rounded font-mono uppercase">Live</span>
                    </h1>
                    <p class="text-[11px] text-slate-400 flex items-center gap-1">
                        <span id="active-count">Mike, Dave, Jessica, Alex, You</span>
                    </p>
                </div>
            </div>

            <div class="flex items-center space-x-3 text-slate-400">
                <button id="sound-toggle" type="button" onclick="toggleSounds()" class="hover:text-amber-400 transition p-2 rounded-full hover:bg-slate-800" title="Mute sounds" aria-label="Mute sounds" aria-pressed="true">
                    <i class="fa-solid fa-volume-high text-sm"></i>
                </button>
                <button title="Start Call" class="hover:text-amber-400 transition p-2 rounded-full hover:bg-slate-800">
                    <i class="fa-solid fa-phone text-sm"></i>
                </button>
                <button title="Video Stream" class="hover:text-amber-400 transition p-2 rounded-full hover:bg-slate-800">
                    <i class="fa-solid fa-video text-sm"></i>
                </button>
            </div>
        </div>

        <!-- MESSAGES FEED CONTAINER -->
        <div id="chat-feed" class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-950/80 relative">
            
            <!-- Date Separator -->
            <div class="flex justify-center my-2">
                <span class="bg-slate-800/80 text-slate-400 text-[11px] px-3 py-1 rounded-full border border-slate-700/50 shadow-sm font-medium">
                    Today
                    <span id="chat-date"></span>
                </span>
            </div>

            <!-- Dynamic Messages will be injected here -->

        </div>

        <!-- TYPING INDICATOR CONTAINER -->
        <div id="typing-indicator" class="px-4 py-1 text-xs text-slate-400 flex items-center space-x-2 bg-slate-950/80 hidden">
            <span id="typing-name" class="font-medium text-slate-300">GM Mike</span>
            <span>is typing</span>
            <div class="flex space-x-1 items-center bg-slate-800 px-2 py-1 rounded-full border border-slate-700">
                <div class="w-1.5 h-1.5 bg-slate-400 rounded-full dot-1"></div>
                <div class="w-1.5 h-1.5 bg-slate-400 rounded-full dot-2"></div>
                <div class="w-1.5 h-1.5 bg-slate-400 rounded-full dot-3"></div>
            </div>
        </div>

        <!-- CHAT INPUT BAR -->
        <div class="bg-slate-900 border-t border-slate-800 p-3 z-10">
            <form id="chat-form" class="flex items-center space-x-2" onsubmit="handleUserSubmit(event)">
                <button type="button" class="text-slate-400 hover:text-amber-400 transition p-2 rounded-full hover:bg-slate-800 flex-shrink-0">
                    <i class="fa-solid fa-circle-plus text-lg"></i>
                </button>
                
                <div class="relative flex-1">
                    <input 
                        type="text" 
                        id="user-input" 
                        placeholder="Type message to work crew..." 
                        class="w-full bg-slate-950 text-slate-100 placeholder-slate-500 text-sm rounded-full pl-4 pr-10 py-2.5 border border-slate-800 focus:outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/50 transition"
                        autocomplete="off"
                    />
                    <button type="button" class="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 transition">
                        <i class="fa-regular fa-face-smile text-base"></i>
                    </button>
                </div>

                <button 
                    type="submit" 
                    class="btn-send bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold p-2.5 rounded-full transition flex items-center justify-center flex-shrink-0"
                    title="Send Message"
                >
                    <i class="fa-solid fa-paper-plane text-sm"></i>
                </button>
            </form>
        </div>

        <div id="call-overlay" class="hidden absolute inset-0 z-30 bg-slate-950/95 flex-col items-center justify-center text-center p-8" role="dialog" aria-modal="true" aria-labelledby="call-title">
            <div id="call-avatar" class="w-24 h-24 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg mb-6"></div>
            <h2 id="call-title" class="text-xl font-bold text-white"></h2>
            <p id="call-status" class="text-sm text-slate-400 mt-2">Incoming audio call...</p>
            <div class="flex items-center gap-12 mt-12">
                <button id="end-call-button" type="button" onclick="endCall()" class="w-14 h-14 rounded-full bg-red-600 hover:bg-red-500 text-white text-xl transition" aria-label="Decline call">
                    <i class="fa-solid fa-phone-slash"></i>
                </button>
                <button id="answer-call-button" type="button" onclick="answerCall()" class="w-14 h-14 rounded-full bg-emerald-500 hover:bg-emerald-400 text-white text-xl transition" aria-label="Answer call">
                    <i class="fa-solid fa-phone"></i>
                </button>
            </div>
        </div>

    </div>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        // Live Clock Implementation
        function updateClock() {
            const now = new Date();
            let hours = now.getHours();
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12; // 0 becomes 12
            document.getElementById('live-clock').textContent = `${hours}:${minutes} ${ampm}`;
        }
        setInterval(updateClock, 1000);
        updateClock();

        // Helper to format timestamps for newly generated messages
        function getFormattedTime() {
            const now = new Date();
            let hours = now.getHours();
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            return `${hours}:${minutes} ${ampm}`;
        }

        function updateChatDate() {
            document.getElementById('chat-date').textContent =
                new Intl.DateTimeFormat('en-US', {
                    month: 'short',
                    day: '2-digit',
                    year: 'numeric'
                }).format(new Date());
        }

        let audioContext = null;
        let soundsEnabled = true;
        let audioUnlocked = false;
        let audioUnlocking = false;
        let callAnswered = false;
        let activeCaller = null;
        let callUtterance = null;
        const typingKeyAudio = new Audio('./iphone-keypress.wav');
        typingKeyAudio.preload = 'auto';
        typingKeyAudio.volume = 0.4;
        const typingAudioClips = new Set();
        const ringtoneAudio = new Audio('./incoming-call-ringtone.mp3');
        ringtoneAudio.loop = true;
        ringtoneAudio.volume = 0.6;

        function unlockAudio() {
            if (audioUnlocked || audioUnlocking) return;

            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (!AudioContextClass) {
                console.error('Web Audio API is not supported in this browser.');
                return;
            }

            audioUnlocking = true;
            try {
                audioContext = audioContext || new AudioContextClass();
                audioContext.resume().then(() => {
                    audioUnlocked = true;
                    audioUnlocking = false;
                    if (soundsEnabled && !document.getElementById('call-overlay').classList.contains('hidden') && !callAnswered) {
                        startRingtone();
                    }
                }).catch(error => {
                    audioUnlocking = false;
                    console.error('Could not unlock audio:', error);
                });
            } catch (error) {
                audioUnlocking = false;
                console.error('Could not unlock audio:', error);
            }
        }

        window.addEventListener('pointerdown', unlockAudio);
        window.addEventListener('keydown', unlockAudio);

        async function toggleSounds() {
            const soundToggle = document.getElementById('sound-toggle');
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;

            if (soundsEnabled) {
                soundsEnabled = false;
                stopRingtone();
                stopTypingSounds();
                if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            } else {
                if (!AudioContextClass) {
                    soundToggle.title = 'Audio is not supported in this browser';
                    console.error('Web Audio API is not supported in this browser.');
                    return;
                }

                try {
                    audioContext = audioContext || new AudioContextClass();
                    await audioContext.resume();
                    audioUnlocked = true;
                    soundsEnabled = true;
                    if (!document.getElementById('call-overlay').classList.contains('hidden') && !callAnswered) {
                        startRingtone();
                    }
                } catch (error) {
                    soundToggle.title = 'Could not enable sounds';
                    console.error('Could not enable chat sounds:', error);
                    return;
                }
            }

            soundToggle.setAttribute('aria-pressed', String(soundsEnabled));
            soundToggle.setAttribute('aria-label', soundsEnabled ? 'Mute sounds' : 'Enable sounds');
            soundToggle.title = soundsEnabled ? 'Mute sounds' : 'Enable sounds';
            soundToggle.innerHTML = `<i class="fa-solid ${soundsEnabled ? 'fa-volume-high' : 'fa-volume-xmark'} text-sm"></i>`;
        }

        function playTone(frequency, duration, volume = 0.06, type = 'sine', startDelay = 0) {
            if (!soundsEnabled || !audioContext) return;

            const oscillator = audioContext.createOscillator();
            const gain = audioContext.createGain();
            const startTime = audioContext.currentTime + startDelay;
            const endTime = startTime + duration;

            oscillator.type = type;
            oscillator.frequency.setValueAtTime(frequency, startTime);
            gain.gain.setValueAtTime(0.0001, startTime);
            gain.gain.exponentialRampToValueAtTime(volume, startTime + 0.01);
            gain.gain.exponentialRampToValueAtTime(0.0001, endTime);
            oscillator.connect(gain);
            gain.connect(audioContext.destination);
            oscillator.start(startTime);
            oscillator.stop(endTime);
        }

        function playTypingSound() {
            if (!soundsEnabled || !audioUnlocked) return;

            const keyAudio = typingKeyAudio.cloneNode();
            keyAudio.volume = typingKeyAudio.volume;
            typingAudioClips.add(keyAudio);
            keyAudio.addEventListener('ended', () => typingAudioClips.delete(keyAudio), { once: true });
            keyAudio.play().catch(error => {
                typingAudioClips.delete(keyAudio);
                console.error('Could not play the typing sound:', error);
            });
        }

        function stopTypingSounds() {
            typingAudioClips.forEach(keyAudio => {
                keyAudio.pause();
                keyAudio.currentTime = 0;
            });
            typingAudioClips.clear();
        }

        function playIncomingMessageSound() {
            const pageIsActive = document.visibilityState === 'visible' && document.hasFocus();

            if (pageIsActive) {
                playTone(880, 0.09, 0.045, 'sine');
            } else {
                playTone(660, 0.12, 0.07, 'sine');
                playTone(880, 0.16, 0.07, 'sine', 0.16);
            }
        }

        function playRingtonePattern() {
            if (!soundsEnabled || !ringtoneAudio.paused) return;

            ringtoneAudio.currentTime = 0;
            ringtoneAudio.play().catch(error => {
                console.error('Could not play the ringtone:', error);
            });
        }

        function startRingtone() {
            if (!soundsEnabled) return;
            playRingtonePattern();
        }

        function stopRingtone() {
            ringtoneAudio.pause();
            if (ringtoneAudio.readyState > 0) ringtoneAudio.currentTime = 0;
        }

        // Crew Members Definitions
        const CREW = {
            mike: {
                name: "GM Mike",
                role: "General Manager",
                avatarColor: "bg-blue-600",
                textColor: "text-blue-400",
                badge: "General Manager"
            },
            jessica: {
                name: "Jessica",
                role: "Shift Lead",
                avatarColor: "bg-purple-600",
                textColor: "text-purple-400",
                badge: "Shift Lead"
            },
            dave: {
                name: "Dave",
                role: "Employee",
                avatarColor: "bg-emerald-600",
                textColor: "text-emerald-400",
                badge: "Employee"
            },
            alex: {
                name: "Alex",
                role: "Cook",
                avatarColor: "bg-orange-600",
                textColor: "text-orange-400",
                badge: "Cook"
            }
        };

        const baseDelay = 1000;
        const delayIncrement = 2500;
        const delayVariance = [baseDelay, baseDelay + delayIncrement, baseDelay + delayIncrement * 2, baseDelay + delayIncrement * 3, baseDelay + delayIncrement * 4, baseDelay + delayIncrement * 5, baseDelay + delayIncrement * 6, baseDelay + delayIncrement * 7, baseDelay + delayIncrement * 8, baseDelay + delayIncrement * 9, baseDelay + delayIncrement * 10];

        // Scripted Crew Scenario
        const scriptMessages = [
            {
                sender: CREW.mike,
                text: "What’s up team?",
                delay: delayVariance[0]
            },
            {
                sender: CREW.jessica,
                text: "Anyone else feeling trapped today? 👍",
                delay: delayVariance[1]
            },
            {
                isUser: true,
                text: "Yes, Meeeee, I need to get out of the apartment and get some fresh air.",
                delay: delayVariance[2]
            },
            {
                sender: CREW.dave,
                text: "Same here. This apartment is killing me. 😅",
                delay: delayVariance[3]
            },
            {
                isUser: true,
                text: "I can not be in the apartment any longer.",
                delay: delayVariance[4]
            },
            {
                sender: CREW.mike,
                text: "I hear you. Anyone need a ride or anything?",
                delay: delayVariance[5]
            },
            {
                isUser: true,
                text: "Someone call me into work please, I need to get out of the apartment, ASAP",
                delay: delayVariance[6]
            },
            {
                isUser: true,
                text: "I will do anything to get out of the apartment.",
                delay: delayVariance[7]
            },
            {
                isUser: true,
                text: "I will work for free. I have to get away from my roommate.",
                delay: delayVariance[8]
            },
            {
                sender: CREW.jessica,
                text: "Gotcha, I'll see what I can do. I will see if I can get you a shift. Hang tight.",
                delay: delayVariance[9]
            },
            {
                isUser: true,
                text: "Thank you so much. I really appreciate it.",
                delay: delayVariance[10]
            }
        ];

        const chatFeed = document.getElementById('chat-feed');
        const typingIndicator = document.getElementById('typing-indicator');
        const typingName = document.getElementById('typing-name');

        // Scroll chat feed to bottom
        function scrollToBottom() {
            chatFeed.scrollTo({
                top: chatFeed.scrollHeight,
                behavior: 'smooth'
            });
        }

        // Render Message Bubble
        function appendMessage(sender, text, isUser = false) {
            const messageWrapper = document.createElement('div');
            messageWrapper.className = `chat-message flex gap-2.5 ${isUser ? 'justify-end' : 'justify-start'} animate-bubble mb-3`;

            const timeStr = getFormattedTime();

            if (isUser) {
                // Outgoing User Message
                messageWrapper.innerHTML = `
                    <div class="max-w-[80%] sm:max-w-[75%] flex flex-col items-end">
                        <div class="bg-amber-500 text-slate-950 font-medium px-4 py-2.5 rounded-2xl rounded-tr-none shadow-md text-sm leading-relaxed border border-amber-400/30 break-words w-full">
                            ${escapeHTML(text)}
                        </div>
                        <div class="flex items-center space-x-1 mt-1 text-[10px] text-slate-400 font-medium">
                            <span>${timeStr}</span>
                            <i class="fa-solid fa-check-double text-amber-500"></i>
                        </div>
                    </div>
                `;
            } else {
                // Incoming Crew Message
                const initials = sender.name.split(' ').map(n => n[0]).join('');
                
                messageWrapper.innerHTML = `
                    <div class="w-8 h-8 rounded-full ${sender.avatarColor} flex items-center justify-center text-white text-xs font-bold shadow-md flex-shrink-0 mt-1">
                        ${initials}
                    </div>
                    <div class="max-w-[80%] sm:max-w-[75%] flex flex-col items-start">
                        <div class="flex items-center space-x-2 mb-1">
                            <span class="text-xs font-semibold ${sender.textColor}">${sender.name}</span>
                            <span class="bg-slate-800 text-slate-400 text-[9px] px-1.5 py-0.2 rounded font-mono">${sender.badge}</span>
                        </div>
                        <div class="bg-slate-800/90 text-slate-100 px-4 py-2.5 rounded-2xl rounded-tl-none shadow-md text-sm leading-relaxed border border-slate-700/60 break-words w-full">
                            ${escapeHTML(text)}
                        </div>
                        <div class="mt-1 text-[10px] text-slate-400 font-medium">
                            ${timeStr}
                        </div>
                    </div>
                `;
            }

            chatFeed.appendChild(messageWrapper);
            scrollToBottom();
            if (!isUser) playIncomingMessageSound();
        }

        // Show / Hide Typing Indicator
        function showTyping(name) {
            typingName.textContent = name;
            typingIndicator.classList.remove('hidden');
            scrollToBottom();
        }

        function hideTyping() {
            typingIndicator.classList.add('hidden');
        }

        function showIncomingCall() {
            const crewMembers = Object.values(CREW);
            activeCaller = crewMembers[Math.floor(Math.random() * crewMembers.length)];
            const callOverlay = document.getElementById('call-overlay');
            const callAvatar = document.getElementById('call-avatar');

            callAnswered = false;
            document.getElementById('call-title').textContent = activeCaller.name;
            callAvatar.className = `w-24 h-24 rounded-full ${activeCaller.avatarColor} flex items-center justify-center text-white text-3xl font-bold shadow-lg mb-6`;
            callAvatar.textContent = activeCaller.name.split(' ').map(name => name[0]).join('');
            document.getElementById('call-status').textContent = 'Incoming audio call...';
            document.getElementById('answer-call-button').classList.remove('hidden');
            document.getElementById('end-call-button').setAttribute('aria-label', 'Decline call');
            callOverlay.classList.remove('hidden');
            callOverlay.classList.add('flex');
            startRingtone();
        }

        function answerCall() {
            callAnswered = true;
            stopRingtone();
            const callStatus = document.getElementById('call-status');
            callStatus.textContent = 'Call connected';
            document.getElementById('answer-call-button').classList.add('hidden');
            document.getElementById('end-call-button').setAttribute('aria-label', 'End call');

            if (!soundsEnabled) {
                callStatus.textContent = 'Call connected — enable sounds to hear the caller';
                return;
            }

            if (!('speechSynthesis' in window)) {
                callStatus.textContent = 'Voice calls are not supported in this browser';
                console.error('Speech Synthesis API is not supported in this browser.');
                return;
            }

            const callLines = {
                'GM Mike': 'Hey, I heard you were looking for a shift. I can get you on the schedule. Can you come in today?',
                Jessica: 'Hey, it is Jessica. I found a shift you can take. Let me know if you are available.',
                Dave: 'Hey, we could use an extra hand at work. Are you able to come in?',
                Alex: 'Hey, I heard you might be able to pick up a shift. Give me a call back when you can.'
            };
            const speech = new SpeechSynthesisUtterance(callLines[activeCaller.name]);
            speech.lang = 'en-US';
            speech.rate = 0.95;
            callUtterance = speech;
            callStatus.textContent = `${activeCaller.name} is speaking...`;
            speech.onend = () => {
                callStatus.textContent = 'Call connected';
                callUtterance = null;
            };
            speech.onerror = event => {
                callStatus.textContent = 'Could not play caller voice';
                console.error('Could not play caller voice:', event.error);
                callUtterance = null;
            };
            window.speechSynthesis.speak(speech);
        }

        function endCall() {
            const callOverlay = document.getElementById('call-overlay');
            if (callOverlay.classList.contains('hidden')) return;

            stopRingtone();
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            callUtterance = null;
            callAnswered = false;
            callOverlay.classList.add('hidden');
            callOverlay.classList.remove('flex');
            chatFeed.querySelectorAll('.chat-message').forEach(message => message.remove());
            document.getElementById('user-input').value = '';
            startConversation();
        }

        // Safe HTML escaping
        function escapeHTML(str) {
            return str.replace(/[&<>'"]/g, 
                tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
            );
        }

        // Execute Scripted Crew Timeline
        async function runCrewScript() {
            let previousDelay = 0;

            for (const msg of scriptMessages) {
                const delay = Math.max(0, msg.delay - previousDelay);

                if (msg.isUser) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                    await typeUserMessage(msg.text);
                } else {
                    const typingDuration = Math.min(1500, delay);
                    await new Promise(resolve => setTimeout(resolve, delay - typingDuration));
                    showTyping(msg.sender.name);
                    await new Promise(resolve => setTimeout(resolve, typingDuration));
                    hideTyping();
                    appendMessage(msg.sender, msg.text, false);
                }

                previousDelay = msg.delay;
            }
        }

        async function typeUserMessage(text) {
            const input = document.getElementById('user-input');
            input.value = '';
            showTyping('You');

            for (const character of text) {
                input.value += character;
                playTypingSound();
                await new Promise(resolve => setTimeout(resolve, 50));
            }

            hideTyping();
            handleUserSubmit({ preventDefault() {} }, false);
        }

        // User Custom Message Handling
        function handleUserSubmit(event, shouldReply = true) {
            event.preventDefault();
            const input = document.getElementById('user-input');
            const text = input.value.trim();

            if (!text) return;

            // Render user message
            appendMessage(null, text, true);
            input.value = '';

            if (!shouldReply) return;

            // Simulated dynamic reply after user input
            setTimeout(() => {
                showTyping(CREW.dave.name);
            }, 1000);

            setTimeout(() => {
                hideTyping();
                appendMessage(
                    CREW.dave, 
                    `Copy that! Thanks for updating the log. Stand by for next status check.`, 
                    false
                );
            }, 2800);
        }

        document.getElementById('user-input').addEventListener('keydown', event => {
            if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
                playTypingSound();
            }
        });

        const callTimer = 1000 * 60 * 0.5; // 30 seconds for call to auto-end if not answered

        // Initialize on load
        async function startConversation() {
            updateChatDate();
            await runCrewScript();
            setTimeout(showIncomingCall, callTimer);
        }

        window.onload = startConversation;
    </script>
</body>
</html>