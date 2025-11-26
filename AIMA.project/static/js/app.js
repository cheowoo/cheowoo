// =========================
// 전역 변수
// =========================
let newMeetingFiles = [],
  analyzedMeetings = [],
  actionItems = [],
  calendar;
let currentMeetingFile = null,
  editIndex = null;

// =========================
// DOM 참조
// =========================
const modal = document.getElementById("fileModal");
const wavList = document.getElementById("wavList");
const newMeetingBtn = document.getElementById("newMeetingBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const listModal = document.getElementById("listModal");
const doneList = document.getElementById("doneList");
const meetingListBtn = document.getElementById("meetingListBtn");
const closeListBtn = document.getElementById("closeListBtn");
const editModal = document.getElementById("editModal");
const editNameEl = document.getElementById("editName");
const editDueEl = document.getElementById("editDue");
const saveEditBtn = document.getElementById("saveEditBtn");
const closeEditBtn = document.getElementById("closeEditBtn");

// =========================
// 함수: 결정사항 렌더링
// =========================
function renderDecisions(decisions) {
  const decEl = document.getElementById("decisions");
  decEl.innerHTML = "";
  (Array.isArray(decisions) ? decisions : []).forEach((d) => {
    const li = document.createElement("li");
    li.textContent = d;
    decEl.appendChild(li);
  });
}

// =========================
// 새 회의 버튼
// =========================
newMeetingBtn.addEventListener("click", async () => {
  modal.style.display = "flex";
  wavList.innerHTML = "<li>🔄 불러오는 중...</li>";
  try {
    const res = await fetch("/api/wav_list");
    const data = await res.json();
    newMeetingFiles = data.files.filter((f) => !analyzedMeetings.includes(f));
    wavList.innerHTML = "";
    newMeetingFiles.forEach((f) => {
      const li = document.createElement("li");
      li.textContent = f;
      li.onclick = () => analyzeFile(f);
      wavList.appendChild(li);
    });
    if (!newMeetingFiles.length)
      wavList.innerHTML = "<li>모든 회의를 분석했습니다 🎉</li>";
  } catch {
    wavList.innerHTML = "<li>❌ 파일 목록을 불러오지 못했습니다.</li>";
  }
});
closeModalBtn.onclick = () => (modal.style.display = "none");

// =========================
// 회의 목록 모달
// =========================
meetingListBtn.onclick = () => {
  listModal.style.display = "flex";
  doneList.innerHTML = analyzedMeetings.length
    ? analyzedMeetings.map((f) => `<li style='cursor:pointer'>📄 ${f}</li>`).join("")
    : "<li>아직 분석 완료된 회의가 없습니다.</li>";
};
closeListBtn.onclick = () => (listModal.style.display = "none");

doneList.addEventListener("click", async (e) => {
  const li = e.target.closest("li");
  if (!li) return;
  const filename = li.textContent.replace("📄", "").trim().replace(".wav", "");
  try {
    const res = await fetch(`/static/data/${filename}.json`);
    if (!res.ok) return alert("❌ 요약본을 찾을 수 없습니다.");
    const data = await res.json();
    currentMeetingFile = filename;
    document.getElementById("topic_summary").value = data.topic_summary || "";
    document.getElementById("content_summary").value = data.content_summary || "";
    renderDecisions(data.decisions);

    actionItems = data.action_items?.length
      ? data.action_items
      : (data.decisions || []).map((d) => ({
          name: "담당자 미상",
          task: d,
          due: null,
        }));

    updateCalendar();
    listModal.style.display = "none";
    alert(`📄 ${filename} 회의 요약을 불러왔습니다.`);
  } catch (err) {
    console.error(err);
    alert("⚠️ 로드 오류");
  }
});

// =========================
// 분석 실행
// =========================
async function analyzeFile(filename) {
  modal.style.display = "none";
  const progressContainer = document.getElementById("progressContainer");
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  const progressPercent = document.getElementById("progressPercent");

  progressContainer.style.display = "block";
  progressBar.style.width = "0%";
  progressText.textContent = "🎧 음성 STT 변환 시작...";
  progressPercent.textContent = "0%";

  try {
    // 1️⃣ 가짜 진행률 (0~90%)
    let progress = 0;
    const timer = setInterval(() => {
      progress = Math.min(progress + Math.random() * 5, 90);
      progressBar.style.width = progress + "%";
      progressPercent.textContent = Math.floor(progress) + "%";

      if (progress < 30) progressText.textContent = "🎧 음성 STT 변환 중...";
      else if (progress < 60) progressText.textContent = "🧠 회의 요약 생성 중...";
      else if (progress < 90) progressText.textContent = "🗓 액션아이템 추출 중...";
    }, 400);

    // 2️⃣ 실제 API 요청
    const res = await fetch("/analyze_meeting", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename }),
    });

    clearInterval(timer);

    if (!res.ok) throw new Error("❌ 분석 실패");

    // 3️⃣ 완료 단계
    progressBar.style.width = "100%";
    progressPercent.textContent = "100%";
    progressText.textContent = "✅ 분석 완료!";

    const data = await res.json();
    currentMeetingFile = filename;
    document.getElementById("topic_summary").value = data.topic_summary || "";
    document.getElementById("content_summary").value = data.content_summary || "";
    renderDecisions(data.decisions);
    actionItems = data.action_items || [];
    updateCalendar();
    analyzedMeetings.push(filename);
    newMeetingFiles = newMeetingFiles.filter((f) => f !== filename);

    // 4️⃣ 완료 후 숨기기
    setTimeout(() => (progressContainer.style.display = "none"), 1500);
    alert(`✅ ${filename} 분석 완료!`);
  } catch (err) {
    console.error(err);
    progressText.textContent = "⚠️ 분석 중 오류 발생";
    progressBar.style.background = "#e74c3c";
    progressPercent.textContent = "오류";
  }
}



// =========================
// 캘린더 초기화
// =========================
document.addEventListener("DOMContentLoaded", () => {
  calendar = new FullCalendar.Calendar(document.getElementById("calendar"), {
    initialView: "dayGridMonth",
    locale: "ko",
    height: 420,
    dateClick: (info) => showTodosModal(info.dateStr),
  });
  calendar.render();
  document.getElementById("closeTodoModalBtn").onclick = () =>
    (document.getElementById("todoModal").style.display = "none");
});

// =========================
// 캘린더/ToDo 갱신
// =========================
function updateCalendar() {
  if (!calendar) return;
  calendar.removeAllEvents();

  const validItems = (actionItems || []).filter((a) => a.due);
  if (validItems.length > 0) {
    calendar.addEventSource(
      validItems.map((a) => ({
        title: `${a.name || "담당자 미상"} — ${a.task}`,
        start: a.due,
        backgroundColor: "#6a4c93",
        borderColor: "#5a3c83",
      }))
    );
  }

  const todoList = document.getElementById("todoList");
  todoList.innerHTML = "";
  if (!actionItems.length) {
    todoList.innerHTML = "<li style='color:#777;'>📭 표시할 ActionItem이 없습니다.</li>";
    return;
  }

  actionItems.forEach((a, i) => {
    const li = document.createElement("li");
    li.innerHTML = `
      👤 <b>${a.name || "담당자 미상"}</b> — ${a.task}
      <span style="margin-left:auto; font-size:13px; color:#555;">
        ${a.due ? "📅 " + a.due : "⏳ 미지정"}
      </span>
      <button class="btn" style="padding:4px 8px;font-size:12px;margin-left:8px"
        onclick="showEditModal(${i})">수정</button>`;
    todoList.appendChild(li);
  });
  calendar.render();
}

// =========================
// 날짜별 ToDo 모달
// =========================
function showTodosModal(dateStr) {
  const todos = actionItems.filter((a) => a.due === dateStr);
  const modal = document.getElementById("todoModal");
  const list = document.getElementById("todoModalList");
  const title = document.getElementById("todoModalTitle");
  title.textContent = `🗓 ${dateStr}의 To-Do List`;
  list.innerHTML = todos.length
    ? todos.map((a) => `<li><input type="checkbox"> 👤 <b>${a.name || "담당자 미상"}</b> — ${a.task}</li>`).join("")
    : "<li>해당 날짜의 할 일이 없습니다.</li>";
  modal.style.display = "flex";
}

// =========================
// 액션아이템 수정 모달
// =========================
function showEditModal(i) {
  editIndex = i;
  const item = actionItems[i];
  editNameEl.value = item.name || "";
  editDueEl.value = item.due || "";
  editModal.style.display = "flex";
}

closeEditBtn.onclick = () => (editModal.style.display = "none");
saveEditBtn.onclick = () => {
  const name = editNameEl.value.trim() || "담당자 미상";
  const due = editDueEl.value || null;
  actionItems[editIndex].name = name;
  actionItems[editIndex].due = due;
  editModal.style.display = "none";
  updateCalendar();

  fetch("/api/update_action_item", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ meeting_file: currentMeetingFile, updated_items: actionItems }),
  });
};
window.showEditModal = showEditModal;
