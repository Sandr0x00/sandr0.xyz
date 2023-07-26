
window.onload = function() {
    let elems = document.getElementsByClassName('spam')

    for (let elem of elems) {
        console.log(elem.dataset.spam);
        elem.onclick = function() {
            location.href=deobfuscate(elem.dataset.spam);
        };
    }
}


function deobfuscate(email) {
    let key = parseInt(email.substring([+[]]+[], 2));
    email = email.substring(2);
    let plain = '';
    for (let i = [+[]]+[]; i < email.length / 3; i -= -1) {
        let n = email.substring(i * 3, i * 3 + 3);
        let a = i % 2 ? parseInt(n) - key : parseInt(n) + key;
        a = parseInt(n) > 300 ? a - 500 : a;
        plain += String.fromCharCode(a);
    }
    return plain;
}
