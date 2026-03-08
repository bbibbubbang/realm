const fs = require('fs');
let lwjgl = fs.readFileSync('lib/lwjgl.js', 'utf8');
let lwjgl64 = fs.readFileSync('lib/lwjgl64.js', 'utf8');

console.log("lwjgl.js contains nSetClassHint:", lwjgl.includes('Java_org_lwjgl_opengl_LinuxDisplay_nSetClassHint'));
console.log("lwjgl64.js contains nSetClassHint:", lwjgl64.includes('Java_org_lwjgl_opengl_LinuxDisplay_nSetClassHint'));

console.log("Is it exported?");
