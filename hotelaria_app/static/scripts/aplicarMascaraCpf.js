const camposCpf = document.getElementsByClassName("campo-cpf");

for(let elemento of camposCpf){
    let valorBase = elemento.innerHTML;
    elemento.innerHTML = `${valorBase.slice(0, 3)}.${valorBase.slice(3, 6)}.${valorBase.slice(6, 9)}-${valorBase.slice(9, 11)}`;
}