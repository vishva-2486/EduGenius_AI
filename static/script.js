const $ = id => document.getElementById(id);
const studyText = () => $("studyText").value.trim();
$("studyText").addEventListener("input", () => $("charCount").textContent = `${$("studyText").value.length} characters`);

async function callApi(url, payload, form = false) {
  const options = form ? {method:"POST", body:payload} : {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)};
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
function busy(btn, on, label="Working...") {
  if (on) { btn.dataset.old = btn.textContent; btn.textContent = label; btn.disabled = true; }
  else { btn.textContent = btn.dataset.old || btn.textContent; btn.disabled = false; }
}
$("uploadBtn").addEventListener("click", async () => {
  const file = $("pdfFile").files[0]; if (!file) { $("uploadStatus").textContent = "Choose a PDF first."; return; }
  const btn=$("uploadBtn"); busy(btn,true,"Reading PDF...");
  try { const form=new FormData(); form.append("file",file); const d=await callApi("/api/upload-pdf",form,true);
    $("studyText").value=d.text; $("charCount").textContent=`${d.text.length} characters`; $("uploadStatus").textContent=`Loaded ${d.filename} (${d.pages} pages).`;
  } catch(e) {$("uploadStatus").textContent=e.message;} finally {busy(btn,false);}
});
$("summaryBtn").addEventListener("click", async () => {
  const btn=$("summaryBtn"); if(studyText().length<20){$("summaryOutput").textContent="Add more study material first.";return;} busy(btn,true);
  try {const d=await callApi("/api/summarize",{text:studyText()}); $("summaryOutput").textContent=d.summary; $("summaryKeywords").replaceChildren();
    d.keywords.forEach(w=>{const tag=document.createElement("span");tag.className="tag";tag.textContent=w;$("summaryKeywords").appendChild(tag);});
  } catch(e){$("summaryOutput").textContent=e.message;} finally{busy(btn,false);}
});
$("answerBtn").addEventListener("click", async () => {
  const btn=$("answerBtn"); if(!studyText()||!$("question").value.trim()){$("answerOutput").textContent="Enter study material and a question.";return;} busy(btn,true);
  try{const d=await callApi("/api/answer",{text:studyText(),question:$("question").value,marks:$("marks").value});$("answerOutput").textContent=d.answer;$("answerNote").textContent=d.note;}
  catch(e){$("answerOutput").textContent=e.message;}finally{busy(btn,false);}
});
$("evaluateBtn").addEventListener("click", async () => {
  const btn=$("evaluateBtn"); if(!studyText()||!$("question").value.trim()||!$("studentAnswer").value.trim()){$("reviewOutput").textContent="Add source material, question and your answer first.";return;} busy(btn,true);
  try{const d=await callApi("/api/evaluate",{question:$("question").value,reference:studyText(),student_answer:$("studentAnswer").value,maximum:$("maxMarks").value});
    $("reviewOutput").textContent=`Estimated keyword score: ${d.estimated_marks} / ${d.maximum}\n\n${d.feedback}\n\nCovered: ${d.covered.join(", ")||"None detected"}\n\nConsider adding: ${d.missing.join(", ")||"No major missing keywords detected"}\n\n${d.disclaimer}`;
  }catch(e){$("reviewOutput").textContent=e.message;}finally{busy(btn,false);}
});
