function changeTheme() {
	var mainlist = document.getElementById("main-list");
	var button = document.getElementById("theme-button");
	var cont = mainlist.parentElement.parentElement;

	if (mainlist.className == "all-websites-main-list row") {
		mainlist.className = "all-websites-main-list-dark row";
		button.className = "theme-button-dark";
		cont.style.backgroundColor = "black";
	} else if (mainlist.className == "all-websites-main-list-dark row") {
		mainlist.className = "all-websites-main-list row";
		button.className = "theme-button-light";
		cont.style.backgroundColor = "white";
	}
}

function changeTheme_ordered() {

	var mainorderedlist = document.getElementById("main-ordered-list");
	var button = document.getElementById("theme-button");
	if (mainorderedlist.className == "all-websites-main-list row") {
		mainorderedlist.className = "all-websites-main-list-dark row";
		button.className = "theme-button-dark";

	} else if (mainorderedlist.className == "all-websites-main-list-dark row") {
		mainorderedlist.className = "all-websites-main-list row";
		button.className = "theme-button-light";
	}

}








