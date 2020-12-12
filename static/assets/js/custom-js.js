var current_theme = document.cookie.replace("theme=","")
if(current_theme=="dark"){
    document.getElementById("main-list").className = "all-websites-main-list-dark row";
    document.getElementById("theme-cont").style.backgroundColor = "black";
    document.getElementById("theme-button").className = "theme-button-dark";
}
function changeTheme() {
	var mainlist = document.getElementById("main-list");
	var button = document.getElementById("theme-button");
	var cont = mainlist.parentElement.parentElement;

	if (mainlist.className == "all-websites-main-list row") {
		mainlist.className = "all-websites-main-list-dark row";
		button.className = "theme-button-dark";
		cont.style.backgroundColor = "black";
        document.cookie = "theme=dark; path=/;";
	} else if (mainlist.className == "all-websites-main-list-dark row") {
		mainlist.className = "all-websites-main-list row";
		button.className = "theme-button-light";
		cont.style.backgroundColor = "white";
        document.cookie = "theme=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
	}
}

