let menu_button = document.getElementById("menu-symbol")
let menu = document.getElementById("mobile-menu")

menu_button.addEventListener("click", () => {
    menu.classList.add("open-menu")
})

menu.addEventListener("click", () => {
    menu.classList.remove("open-menu")
})