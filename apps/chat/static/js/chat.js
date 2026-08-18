/* ==========================================================
   DocCompanion
   chat.js
   Phase 4.1

   Initialization
   CSRF
   Utilities
   Sidebar
   Auto Resize
   Keyboard
========================================================== */

"use strict";

let deleteConversationId = null;

/* ==========================================================
    APPLICATION
========================================================== */

const ChatApp = {

    currentConversation: null,

    isSending: false,

    csrfToken: null,

    initialized: false

};


/* ==========================================================
    ELEMENTS
========================================================== */

const promptInput =
    document.getElementById("promptInput");

const sendButton =
    document.getElementById("sendButton");

const chatContainer =
    document.getElementById("chatContainer");

const typingIndicator =
    document.getElementById("typingIndicator");

const processingLabel =
    document.getElementById("processingLabel");

const newChatButton =
    document.getElementById("newChatBtn");

const uploadButton =
    document.getElementById("uploadBtn");

const historyList =
    document.getElementById("historyList");

const documentList =
    document.getElementById("documentList");

const sidebar =
    document.querySelector(".sidebar");

const conversationTitle =
    document.getElementById("conversationTitle");

let processingStateTimer = null;


/* ==========================================================
    DOM READY
========================================================== */

document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);


/* ==========================================================
    INITIALIZE
========================================================== */

function initializeApplication() {

    if (ChatApp.initialized)
        return;

    ChatApp.initialized = true;

    ChatApp.csrfToken = getCSRFToken();

    registerEvents();

    autoResizeTextarea();

    console.log(
        "DocCompanion initialized."
    );

}


/* ==========================================================
    REGISTER EVENTS
========================================================== */

function registerEvents() {

    if (promptInput) {

        promptInput.addEventListener(
            "input",
            autoResizeTextarea
        );

        promptInput.addEventListener(
            "keydown",
            handleKeyboard
        );

    }

    if (sendButton) {

        sendButton.addEventListener(
            "click",
            function () {

                if (typeof sendMessage === "function") {

                    sendMessage();

                }

            }
        );

    }

    if (newChatButton) {

        newChatButton.addEventListener(
            "click",
            function () {

                if (typeof createNewChat === "function") {

                    createNewChat();

                }

            }
        );

    }

    if (uploadButton) {

        uploadButton.addEventListener(
            "click",
            function () {

                if (typeof uploadDocuments === "function") {

                    uploadDocuments();

                }

            }
        );

    }

}


/* ==========================================================
    CSRF TOKEN
========================================================== */

function getCSRFToken() {

    const cookie =
        document.cookie
            .split(";")
            .find(
                item =>
                item.trim().startsWith("csrftoken=")
            );

    if (!cookie)
        return "";

    return cookie.split("=")[1];

}


/* ==========================================================
    FETCH WRAPPER
========================================================== */

async function apiRequest(
    url,
    method = "GET",
    data = null
) {

    const options = {

        method: method,

        headers: {

            "X-CSRFToken":
                ChatApp.csrfToken,

            "X-Requested-With":
                "XMLHttpRequest"

        }

    };

    if (data instanceof FormData) {

        options.body = data;

    }
    else if (data !== null) {

        options.headers[
            "Content-Type"
        ] = "application/json";

        options.body =
            JSON.stringify(data);

    }

    const response =
        await fetch(url, options);

    if (!response.ok) {

        throw new Error(
            "Request failed."
        );

    }

    return await response.json();

}


/* ==========================================================
    AUTO RESIZE
========================================================== */

function autoResizeTextarea() {

    if (!promptInput)
        return;

    promptInput.style.height = "auto";

    promptInput.style.height =
        Math.min(
            promptInput.scrollHeight,
            180
        ) + "px";

}


/* ==========================================================
    KEYBOARD
========================================================== */

function handleKeyboard(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        if (
            typeof sendMessage === "function"
        ) {

            sendMessage();

        }

    }

}


/* ==========================================================
    SIDEBAR
========================================================== */

function openSidebar() {

    if (!sidebar)
        return;

    sidebar.classList.add("show");

}

function closeSidebar() {

    if (!sidebar)
        return;

    sidebar.classList.remove("show");

}

function toggleSidebar() {

    if (!sidebar)
        return;

    sidebar.classList.toggle("show");

}


/* ==========================================================
    LOADING
========================================================== */
function showProcessingState(message = "Searching your documents…") {
    if (!typingIndicator)
        return;

    if (processingLabel)
        processingLabel.textContent = message;

    typingIndicator.classList.remove("d-none");
    typingIndicator.setAttribute("aria-hidden", "false");
    scrollToBottom();

    window.clearTimeout(processingStateTimer);
    processingStateTimer = window.setTimeout(
        () => setProcessingState("Still working locally…"),
        12000
    );
}

function setProcessingState(message) {
    if (processingLabel)
        processingLabel.textContent = message;
}

function hideProcessingState() {
    if (!typingIndicator)
        return;

    window.clearTimeout(processingStateTimer);
    processingStateTimer = null;
    typingIndicator.classList.add("d-none");
    typingIndicator.setAttribute("aria-hidden", "true");
}

/* ==========================================================
    SCROLL
========================================================== */

function scrollToBottom() {

    if (!chatContainer)
        return;

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}


/* ==========================================================
    BUTTON STATE
========================================================== */

function disableSendButton() {

    if (!sendButton)
        return;

    ChatApp.isSending = true;

    sendButton.disabled = true;
    sendButton.classList.add("is-loading");
    sendButton.setAttribute("aria-label", "Processing request");
    sendButton.innerHTML = '<span class="send-spinner" aria-hidden="true"></span>';

}

function enableSendButton() {

    if (!sendButton)
        return;

    ChatApp.isSending = false;

    sendButton.disabled = false;
    sendButton.classList.remove("is-loading");
    sendButton.setAttribute("aria-label", "Send message");
    sendButton.innerHTML = '<i class="bi bi-arrow-up"></i>';

}


/* ==========================================================
    ESCAPE HTML
========================================================== */

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;

}


/* ==========================================================
    UUID
========================================================== */

function uuid() {

    return crypto.randomUUID();

}


/* ==========================================================
    DATE FORMAT
========================================================== */

function formatTime(date = new Date()) {

    return date.toLocaleTimeString(
        [],
        {

            hour: "2-digit",

            minute: "2-digit"

        }
    );

}


/* ==========================================================
    MESSAGE ID
========================================================== */

function messageId() {

    return "msg-" + uuid();

}


/* ==========================================================
    PLACEHOLDER FUNCTIONS

    (Implemented in Phase 4.2+)
========================================================== */

async function sendMessage() {

    console.log(
        "Phase 4.2"
    );

}

async function createNewChat() {

    console.log(
        "Phase 4.3"
    );

}

async function uploadDocuments() {

    console.log(
        "Phase 4.4"
    );

}


/* ==========================================================
    DEBUG
========================================================== */

console.log(
    "chat.js loaded."
);

/* ==========================================================
   Phase 4.2
   Chat Messaging
========================================================== */


/* ==========================================================
    SEND MESSAGE
========================================================== */

/* ==========================================================
   STREAM MESSAGE
========================================================== */

async function sendMessage() {

    if (ChatApp.isSending)
        return;

    const prompt = promptInput.value.trim();

    if (!prompt)
        return;

    appendUserMessage(prompt);

    promptInput.value = "";

    autoResizeTextarea();

    disableSendButton();

    showProcessingState("Searching your documents…");

    scrollToBottom();

    let assistantStarted = false;

    try {

        const response = await fetch(

            "/chat/stream/",

            {

                method: "POST",

                headers: {

                    "Content-Type": "application/json",

                    "X-CSRFToken": ChatApp.csrfToken,

                },

                body: JSON.stringify({

                    prompt: prompt,

                    conversation_id:
                        ChatApp.currentConversation,

                }),

            }

        );

        if (!response.ok) {

            throw new Error("Streaming failed.");

        }

        const responseConversationId =
            response.headers.get("X-Conversation-ID");

        if (responseConversationId) {
            ChatApp.currentConversation = responseConversationId;
        }

        setProcessingState("Generating your answer…");

        const reader =
            response.body.getReader();

        const decoder =
            new TextDecoder();

        let answer = "";

        while (true) {
            const {done, value} = await reader.read();

            if (done)
                break;

            const token = decoder.decode(value, {stream: true});
            if (!token)
                continue;

            if (!assistantStarted) {
                hideProcessingState();
                appendAssistantMessage("");
                assistantStarted = true;
            }

            answer += token;
            updateLastAssistantMessage(answer);
            scrollToBottom();
        }

        hideProcessingState();

        if (!assistantStarted) {
            appendAssistantMessage(
                "No response was produced. Please try your question again."
            );
        }

        await refreshHistory();

        if (ChatApp.currentConversation) {
            await loadConversation(ChatApp.currentConversation);
        }

        enableSendButton();
    }
    catch (error) {
        console.error(error);
        hideProcessingState();
        enableSendButton();

        if (assistantStarted) {
            updateLastAssistantMessage(
                "⚠️ Unable to complete the response. Please try again."
            );
        }
        else {
            appendAssistantMessage(
                "⚠️ Unable to contact the AI assistant."
            );
        }
    }
}


/* ==========================================================
    USER MESSAGE
========================================================== */

function appendUserMessage(text, createdAt = null) {

    const time = formatMessageTime(createdAt);

    const html = `

        <div class="message user-message fade-in">

            <div class="message-body">

                <div class="message-meta">
                    <strong>You</strong>
                    <span>${time}</span>
                </div>

                <div class="message-content">

                    ${escapeHTML(text)}

                </div>

            </div>

        </div>

    `;

    chatContainer.insertAdjacentHTML(

        "beforeend",

        html

    );

    scrollToBottom();

}


/* ==========================================================
    ASSISTANT MESSAGE
========================================================== */

function appendAssistantMessage(text, citations = [], createdAt = null) {

    const time = formatMessageTime(createdAt);

    let sourceHtml = "";
    if (citations.length) {
        sourceHtml += `
            <div class="citation-box">
                <div class="citation-title">
                    Sources
                </div>
                <ul>
        `;
        citations.forEach(c => {
            const pages = Array.isArray(c.pages)
                ? c.pages
                : (c.page ? [c.page] : []);
            const pageLabel = pages.length > 1
                ? `Pages ${pages.join(", ")}`
                : (pages.length === 1 ? `Page ${pages[0]}` : "");

            sourceHtml += `
                <li>
                    📄 ${escapeHTML(c.document)}
                    ${pageLabel ? `(${escapeHTML(pageLabel)})` : ""}
                </li>
            `;
        });
        sourceHtml += `
                </ul>
            </div>
        `;
    }

    chatContainer.insertAdjacentHTML(
        "beforeend",
        `
        <div class="message assistant-message">
            <div class="avatar"><i class="bi bi-stars"></i></div>
            <div class="message-body">
                <div class="message-meta">
                    <strong>DocCompanion</strong>
                    <span>${time}</span>
                </div>
                <div class="message-content">
                    ${renderMarkdown(text)}
                    ${sourceHtml}
                </div>
            </div>
        </div>
        `
    );
}


/* ==========================================================
    MARKDOWN
========================================================== */

function renderMarkdown(text) {

    if (

        typeof marked !== "undefined"

    ) {

        return marked.parse(text);

    }

    return escapeHTML(text)

        .replace(/\n/g, "<br>");

}


/* ==========================================================
    CLEAR CHAT
========================================================== */

function clearConversation() {

    chatContainer.innerHTML = "";

}


/* ==========================================================
    LOADING MESSAGE
========================================================== */

function appendLoadingMessage() {

    const html = `

        <div
            id="loadingMessage"
            class="message assistant-message">

            <div class="avatar">

                <i class="bi bi-robot"></i>

            </div>

            <div class="message-body">

                <div class="message-content">

                    Thinking...

                </div>

            </div>

        </div>

    `;

    chatContainer.insertAdjacentHTML(

        "beforeend",

        html

    );

}


function removeLoadingMessage() {

    const loading =

        document.getElementById(

            "loadingMessage"

        );

    if (loading)

        loading.remove();

}


/* ==========================================================
    UPDATE MESSAGE
========================================================== */

function updateLastAssistantMessage(text) {
    const messages = document.querySelectorAll(".assistant-message .message-content");

    if (!messages.length)
        return;
    const last = messages[messages.length - 1];
    last.innerHTML = renderMarkdown(text);
}


/* ==========================================================
    ERROR MESSAGE
========================================================== */

function showError(text) {

    appendAssistantMessage(

        "❌ " + text

    );

}


/* ==========================================================
    SUCCESS
========================================================== */

function showSuccess(text) {

    console.log(

        text

    );

}


/* ==========================================================
    COPY CODE
========================================================== */

document.addEventListener(

    "click",

    function(event){

        const button =

            event.target.closest(

                ".copy-code"

            );

        if(!button)

            return;

        const code =

            button.nextElementSibling.innerText;

        navigator.clipboard.writeText(

            code

        );

        button.innerHTML =

            '<i class="bi bi-check"></i>';

        setTimeout(

            ()=>{

                button.innerHTML=

                    '<i class="bi bi-copy"></i>';

            },

            1500

        );

    }

);


/* ==========================================================
    AUTO SCROLL
========================================================== */

const observer =

    new MutationObserver(

        function(){

            scrollToBottom();

        }

    );

observer.observe(

    chatContainer,

    {

        childList:true

    }

);


/* ==========================================================
    HELLO MESSAGE
========================================================== */

function showWelcomeMessage(){

    if(

        chatContainer.children.length===0

    ){

        appendAssistantMessage(

            "Hello 👋\n\nI am DocCompanion. Ask anything about your indexed documents."

        );

    }

}


function formatMessageTime(value) {
    const date = value ? new Date(value) : new Date();

    if (Number.isNaN(date.getTime()))
        return "";

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


function setConversationTitle(title) {
    if (conversationTitle)
        conversationTitle.textContent = title || "New conversation";
}


/* ==========================================================
    INITIAL MESSAGE
========================================================== */

showWelcomeMessage();

/* ==========================================================
   Phase 4.3
   Conversation Management
========================================================== */


/* ==========================================================
    NEW CHAT
========================================================== */

async function createNewChat() {

    if (ChatApp.isSending)
        return;

    try {

        const response = await apiRequest(

            "/chat/new/",

            "POST"

        );

        ChatApp.currentConversation =

            response.conversation_id;

        clearConversation();

        showWelcomeMessage();

        setConversationTitle("New conversation");

        removeActiveConversation();

        prependConversation(

            response.conversation_id,

            "New Chat"

        );

    }

    catch (error) {

        console.error(error);

        showError(

            "Unable to create a new conversation."

        );

    }

}


/* ==========================================================
    LOAD HISTORY
========================================================== */

async function loadHistory() {
    try {
        const history = await apiRequest("/chat/history/", "GET");
        historyList.innerHTML = "";

        if (!history.length) {
            historyList.innerHTML = `
                <div class="history-empty">
                    <i class="bi bi-chat-square"></i>
                    <span>No conversations yet</span>
                </div>
            `;
            return;
        }

        history.forEach(
            conversation => {
                appendConversation(conversation);
            }
        );

        if (ChatApp.currentConversation) {
            setConversationActive(ChatApp.currentConversation);
        }
    }
    catch (error) {
        console.error(error);
    }
}


/* ==========================================================
    LOAD CONVERSATION
========================================================== */

async function loadConversation(

    conversationId

) {

    try {

        const response = await apiRequest(

            `/chat/${conversationId}/`,

            "GET"

        );

        ChatApp.currentConversation =

            conversationId;

        clearConversation();

        response.messages.forEach(

            message => {

                if (

                    message.role === "user"

                ) {

                    appendUserMessage(

                        message.content,
                        message.created_at

                    );

                }

                else {
                    appendAssistantMessage(
                        message.content,
                        message.citations || [],
                        message.created_at
                    );
                }

            }

        );

        setConversationActive(

            conversationId

        );

        setConversationTitle(response.conversation.title);

        if (!response.messages.length) {
            showWelcomeMessage();
        }

        if (window.innerWidth < 992) {
            closeSidebar();
        }

    }

    catch (error) {

        console.error(error);

    }

}


/* ==========================================================
    SIDEBAR
========================================================== */

function appendConversation(

    conversation

) {

    const html = `

        <a
            href="#"
            class="history-item"
            data-id="${conversation.id}">

            <span>
                <i class="bi bi-chat-square-text"></i>
                <span class="history-title">${escapeHTML(conversation.title)}</span>
            </span>
            <button class="delete-chat" type="button" aria-label="Delete ${escapeHTML(conversation.title)}">
                <i class="bi bi-trash"></i>
            </button>

        </a>

    `;

    historyList.insertAdjacentHTML(

        "beforeend",

        html

    );

}


function prependConversation(

    id,

    title

) {

    const html = `

        <a
            href="#"
            class="history-item active"
            data-id="${id}">

            <span>
                <i class="bi bi-chat-square-text"></i>
                <span class="history-title">${escapeHTML(title)}</span>
            </span>
            <button class="delete-chat" type="button" aria-label="Delete ${escapeHTML(title)}">
                <i class="bi bi-trash"></i>
            </button>

        </a>

    `;

    historyList.insertAdjacentHTML(

        "afterbegin",

        html

    );

}


/* ==========================================================
    ACTIVE CHAT
========================================================== */

function removeActiveConversation() {

    document

        .querySelectorAll(

            ".history-item"

        )

        .forEach(

            item =>

            item.classList.remove(

                "active"

            )

        );

}


function setConversationActive(

    id

) {

    removeActiveConversation();

    const item =

        document.querySelector(

            `.history-item[data-id="${id}"]`

        );

    if (item) {

        item.classList.add(

            "active"

        );

        const titleElement = item.querySelector(".history-title");
        if (titleElement)
            setConversationTitle(titleElement.textContent);
    }

}


/* ==========================================================
    CLICK HISTORY
========================================================== */

historyList.addEventListener(

    "click",

    function (event) {

        if (event.target.closest(".delete-chat"))
            return;

        const item =

            event.target.closest(

                ".history-item"

            );

        if (!item)

            return;

        event.preventDefault();

        loadConversation(

            item.dataset.id

        );

    }

);


/* ==========================================================
    DELETE
========================================================== */

function showDeleteConversationModal(conversationId){
    deleteConversationId = conversationId;
    const modal = new bootstrap.Modal(
        document.getElementById("deleteConversationModal")
    );
    modal.show();
}

async function deleteConversation(conversationId){

    try{

        await apiRequest(

            `/chat/delete/${conversationId}/`,

            "DELETE"

        );

        const item=document.querySelector(

            `.history-item[data-id="${conversationId}"]`

        );

        if(item){

            item.remove();

        }

        if(ChatApp.currentConversation==conversationId){

            ChatApp.currentConversation=null;

            clearConversation();

            showWelcomeMessage();

            setConversationTitle("New conversation");

        }

        await loadHistory();

    }

    catch(error){

        console.error(error);

        showError(

            "Unable to delete conversation."

        );

    }

}


/* ==========================================================
    CONTEXT MENU
========================================================== */

historyList.addEventListener(

    "contextmenu",

    function(event){

        const item=

            event.target.closest(

                ".history-item"

            );

        if(!item)

            return;

        event.preventDefault();

        showDeleteConversationModal(item.dataset.id);
    }
);


/* ==========================================================
    AUTO TITLE
========================================================== */

function updateConversationTitle(

    title

){

    if(

        !ChatApp.currentConversation

    )

        return;

    const item=

        document.querySelector(

            `.history-item[data-id="${ChatApp.currentConversation}"]`

        );

    if(item){

        const titleElement = item.querySelector(".history-title");
        if (titleElement)
            titleElement.textContent = title;

    }

    setConversationTitle(title);

}


/* ==========================================================
    RENAME
========================================================== */

function renameConversation(

    id,

    title

){

    const item=

        document.querySelector(

            `.history-item[data-id="${id}"]`

        );

    if(item){

        const titleElement = item.querySelector(".history-title");
        if (titleElement)
            titleElement.textContent = title;

    }

}


/* ==========================================================
    REFRESH
========================================================== */

async function refreshHistory(){
    await loadHistory();
}
/* ==========================================================
    INITIAL LOAD
========================================================== */

loadHistory();

document.getElementById("confirmDeleteConversation").addEventListener(

    "click",

    async function(){

        if(deleteConversationId){

            await deleteConversation(

                deleteConversationId

            );

        }

        bootstrap.Modal.getInstance(

            document.getElementById(

                "deleteConversationModal"

            )

        ).hide();

        deleteConversationId=null;

    }

);

historyList.addEventListener(

    "click",

    function(event){

        if(

            event.target.closest(".delete-chat")

        ){

            event.stopPropagation();
            event.preventDefault();

            const item=

                event.target.closest(

                    ".history-item"

                );

            showDeleteConversationModal(

                item.dataset.id

            );

        }

    }

);


/* ==========================================================
   Phase 4.4
   Documents
   Search
   Notifications
   Final Initialization
========================================================== */


/* ==========================================================
    DOCUMENT UPLOAD
========================================================== */
async function uploadDocuments() {
    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);
    const fileInput = form.querySelector("input[type=file]");
    if (!fileInput.files.length) {
        showToast("Please select at least one document.", "warning");
        return;
    }

    try {
        uploadButton.disabled = true;
        uploadButton.innerHTML =`<span class="spinner-border spinner-border-sm"></span>Uploading...`;
        await apiRequest("/documents/upload/", "POST", formData);
        showToast("Documents uploaded successfully.", "success");
        bootstrap.Modal.getInstance(document.getElementById("uploadModal")).hide();

        form.reset();
        refreshDocumentList();
    }
    catch (error) {
        console.error(error);
        showToast("Upload failed.", "danger");
    }
    finally {
        uploadButton.disabled = false;
        uploadButton.innerHTML = `<i class="bi bi-cloud-upload"></i> Upload`;
    }
}


/* ==========================================================
    DOCUMENT LIST
========================================================== */

async function refreshDocumentList() {

    try {

        const docs = await apiRequest(

            "/documents/list/",

            "GET"

        );

        documentList.innerHTML = "";

        docs.forEach(

            doc => {

                appendDocument(doc);

            }

        );

    }

    catch (error) {

        console.error(error);

    }

}


function appendDocument(doc) {

    const icon = getDocumentIcon(

        doc.file_type

    );

    const html = `

        <div
            class="document-item"
            data-id="${doc.id}">

            <div>

                <i class="bi ${icon}"></i>

                ${escapeHTML(doc.name)}

            </div>

            <i
                class="bi bi-trash delete-document">
            </i>

        </div>

    `;

    documentList.insertAdjacentHTML(

        "beforeend",

        html

    );

}


/* ==========================================================
    ICONS
========================================================== */

function getDocumentIcon(type){

    switch(type){

        case "pdf":
            return "bi-file-earmark-pdf";

        case "docx":
            return "bi-file-earmark-word";

        case "pptx":
            return "bi-file-earmark-ppt";

        case "xlsx":
            return "bi-file-earmark-excel";

        case "csv":
            return "bi-file-earmark-spreadsheet";

        default:
            return "bi-file-earmark-text";

    }

}


/* ==========================================================
    SEARCH
========================================================== */

const documentSearch =

    document.querySelector(

        ".sidebar input"

    );

if(documentSearch){

    documentSearch.addEventListener(

        "keyup",

        function(){

            const keyword=

                this.value

                .toLowerCase();

            document

                .querySelectorAll(

                    ".document-item"

                )

                .forEach(

                    item=>{

                        item.style.display=

                            item.innerText

                            .toLowerCase()

                            .includes(keyword)

                            ? ""

                            : "none";

                    }

                );

        }

    );

}


/* ==========================================================
    DELETE DOCUMENT
========================================================== */

documentList.addEventListener(

    "click",

    function(event){

        const button=

            event.target.closest(

                ".delete-document"

            );

        if(!button)

            return;

        event.stopPropagation();

        const id=

            button

            .closest(

                ".document-item"

            )

            .dataset.id;

        showDeleteDocumentModal(id);

    }

);


/* ==========================================================
    DELETE MODAL
========================================================== */

let deleteDocumentId=null;

function showDeleteDocumentModal(id){

    deleteDocumentId=id;

    const modal=

        new bootstrap.Modal(

            document.getElementById(

                "deleteDocumentModal"

            )

        );

    modal.show();

}


document

.getElementById(

    "confirmDeleteDocument"

)

.addEventListener(

    "click",

    async function(){

        await deleteDocument(

            deleteDocumentId

        );

        bootstrap.Modal.getInstance(

            document.getElementById(

                "deleteDocumentModal"

            )

        ).hide();

    }

);


async function deleteDocument(id){

    try{

        await apiRequest(

            `/documents/delete/${id}/`,

            "DELETE"

        );

        showToast(

            "Document deleted.",

            "success"

        );

        refreshDocumentList();

    }

    catch(error){

        showToast(

            "Unable to delete document.",

            "danger"

        );

    }

}


/* ==========================================================
    DRAG & DROP
========================================================== */

const uploadBox=

    document.querySelector(

        ".upload-box"

    );

if(uploadBox){

    uploadBox.addEventListener(

        "dragover",

        function(e){

            e.preventDefault();

            this.classList.add(

                "border-primary"

            );

        }

    );

    uploadBox.addEventListener(

        "dragleave",

        function(){

            this.classList.remove(

                "border-primary"

            );

        }

    );

    uploadBox.addEventListener(

        "drop",

        function(e){

            e.preventDefault();

            this.classList.remove(

                "border-primary"

            );

            const files=

                e.dataTransfer.files;

            document

                .querySelector(

                    "#uploadForm input[type=file]"

                )

                .files=files;

        }

    );

}


/* ==========================================================
    TOAST
========================================================== */

function showToast(

    message,

    type="success"

){

    const toast=document.createElement("div");

    toast.className=

        `toast align-items-center text-bg-${type}
         border-0 show position-fixed
         bottom-0 end-0 m-4`;

    toast.style.zIndex=3000;

    toast.innerHTML=`

        <div class="d-flex">

            <div class="toast-body">

                ${message}

            </div>

            <button
                class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast">
            </button>

        </div>

    `;

    document.body.appendChild(toast);

    setTimeout(

        ()=>toast.remove(),

        3000

    );

}


/* ==========================================================
    FINAL INIT
========================================================== */

function initializeUI(){

    refreshDocumentList();

    loadHistory();

    showWelcomeMessage();

}

initializeUI();
