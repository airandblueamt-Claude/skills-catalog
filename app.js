/* Renders the catalog from skills.json. No build step, no dependencies. */

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

function cardHTML(s, i) {
  const tags = (s.tags || [])
    .map((t) => `<span class="tag">${esc(t)}</span>`)
    .join("");
  return `
  <article class="card" style="animation-delay:${i * 90}ms">
    <div class="card__top">
      <span class="card__ref">${esc(s.ref || "")}</span>
      <span class="card__status">${esc(s.status || "")}</span>
    </div>
    <h3 class="card__name">${esc(s.name)}</h3>
    <p class="card__summary">${esc(s.summary)}</p>
    ${
      s.use_when
        ? `<p class="card__usewhen"><b>Use when</b>${esc(s.use_when)}</p>`
        : ""
    }
    <div class="card__tags">${tags}</div>
    <div class="card__actions">
      <a class="btn btn--primary" href="${esc(s.repo)}" target="_blank" rel="noopener">View on GitHub ↗</a>
      ${
        s.install
          ? `<button class="btn btn--copy btn--ghost" data-install="${esc(
              s.install
            )}" title="Copy install command">Copy install</button>`
          : ""
      }
    </div>
  </article>`;
}

function useRowHTML(s, i) {
  return `
  <a class="use-row" href="${esc(s.link || "#")}" target="_blank" rel="noopener" style="animation-delay:${
    i * 60
  }ms">
    <span class="use-row__name">${esc(s.name)}</span>
    <span class="use-row__summary">${esc(s.summary)}</span>
    <span class="use-row__author">${esc(s.author || "")}</span>
  </a>`;
}

function pad(n) {
  return String(n).padStart(2, "0");
}

async function main() {
  let data;
  try {
    const res = await fetch("skills.json", { cache: "no-cache" });
    data = await res.json();
  } catch (e) {
    document.getElementById("mineCards").innerHTML =
      '<p class="card__summary">Could not load skills.json.</p>';
    return;
  }

  // header
  document.getElementById("tagline").textContent = data.owner?.tagline || "";
  const gh = document.getElementById("ghLink");
  gh.href = data.owner?.github || "#";
  document.getElementById("ghHandle").textContent =
    data.owner?.handle || "github";

  // my skills
  const mine = data.mine || [];
  document.getElementById("mineCards").innerHTML = mine
    .map((s, i) => cardHTML(s, i))
    .join("");
  document.getElementById("mineCount").textContent = `${pad(mine.length)} ITEM${
    mine.length === 1 ? "" : "S"
  }`;

  // skills i use
  const uses = data.uses || [];
  const usesSection = document.getElementById("usesSection");
  if (uses.length === 0) {
    usesSection.style.display = "none";
  } else {
    document.getElementById("usesList").innerHTML = uses
      .map((s, i) => useRowHTML(s, i))
      .join("");
    document.getElementById("usesCount").textContent = `${pad(uses.length)} ITEM${
      uses.length === 1 ? "" : "S"
    }`;
  }

  // copy-install interaction
  document.addEventListener("click", async (ev) => {
    const btn = ev.target.closest(".btn--copy");
    if (!btn) return;
    try {
      await navigator.clipboard.writeText(btn.dataset.install);
      const old = btn.textContent;
      btn.textContent = "Copied ✓";
      btn.classList.add("copied");
      setTimeout(() => {
        btn.textContent = old;
        btn.classList.remove("copied");
      }, 1600);
    } catch (e) {
      /* clipboard blocked — ignore */
    }
  });
}

main();
