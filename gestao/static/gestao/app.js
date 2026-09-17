// Botão "A+": alterna letra ampliada e lembra a escolha neste aparelho.
(function () {
  var CHAVE = "letra-grande";
  var raiz = document.documentElement;

  function ler() {
    try { return localStorage.getItem(CHAVE) === "1"; } catch (e) { return false; }
  }
  function aplicar(ligado) {
    raiz.classList.toggle("letra-grande", ligado);
    document.querySelectorAll("[data-letra]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(ligado));
    });
  }

  aplicar(ler());
  document.addEventListener("click", function (ev) {
    var botao = ev.target.closest("[data-letra]");
    if (!botao) return;
    var ligado = !raiz.classList.contains("letra-grande");
    aplicar(ligado);
    try { localStorage.setItem(CHAVE, ligado ? "1" : "0"); } catch (e) { /* sem armazenamento: vale só nesta página */ }
  });
})();
