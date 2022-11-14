var i = 0;
var img = [];
var time = 1200;

img[0] = "imgs/banner1.jpg";
img[1] = "imgs/banner5.jpg";
img[2] = "imgs/banner3.png";
img[3] = "imgs/banner4.jpg";
img[4] = "imgs/medical.jpg";

function img_change() {

    document.slide.src = img[i];
    if (i < img.length - 1) {
        i++;
    } else {
        i = 0;
    }
    setTimeout(img_change, time);
}
window.onload = img_change;