
var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
	
  var currentScrollPos = window.pageYOffset;
  if (prevScrollpos > currentScrollPos) {
   document.getElementById("nav-b").style.top = "0";
  } else {
   document.getElementById("nav-b").style.top = "-60px";
  }
  prevScrollpos = currentScrollPos;
}

function changeTheme(){
var mainlist = document.getElementById("main-list");
var button = document.getElementById("theme-button");
	
	if (mainlist.className=="no-space all-websites-main-list row" ){
			mainlist.className = "no-space all-websites-main-list-dark row";
			button.className = "theme-button-dark";
			
	}else if(mainlist.className == "no-space all-websites-main-list-dark row"){
			mainlist.className = "no-space all-websites-main-list row";
			button.className = "theme-button-light";
			
	}
}



function changeTheme_ordered(){
	
	var mainorderedlist = document.getElementById("main-ordered-list");
var button = document.getElementById("theme-button");
	if(mainorderedlist.className == "all-websites-main-list row"){
			mainorderedlist.className = "all-websites-main-list-dark row";
			button.className = "theme-button-dark";
			
	}else if(mainorderedlist.className == "all-websites-main-list-dark row"){
			mainorderedlist.className = "all-websites-main-list row";
			button.className = "theme-button-light";
	}

}




	



