
// alert("org_name="+window.localStorage.getItem('name'));
// alert("org_password="+window.localStorage.getItem('password'));
// alert("org_email="+window.localStorage.getItem('email'));



document.getElementById('org_name').addEventListener('submit',function(e){
	e.preventDefault();
	
	//const formdata1 = new FormData();
	let data1= new FormData();
    const name2 = document.getElementById('uname').value;
    
    const password2 = document.getElementById('pass').value;
    	
	org_login(name2,password2);
	
});


function org_login(email,password){  
    var json_data_org_login = {
        "email":email,
        "password":password
    };
var data_org_login = JSON.stringify(json_data_org_login);
console.log(data_org_login);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/org/login";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        window.token = json['token'];
        console.log(json);
        window.localStorage.setItem('org_token',json.token);
        //hideLoader();
        //alert("org_token="+window.localStorage.getItem('org_token'));
        window.location = "./index_dash.html";
    }
}   
xhr.send(data_org_login);
}




