function create_api(token,x){  
    var json_data_org_create_api = {
        "token":token,
		
        "description":x
    };
var data_create_api = JSON.stringify(json_data_org_create_api);
console.log(data_create_api);
    //showLoader();
xhr = new XMLHttpRequest();
var url = "http://52.203.240.40:8080/org/user_listing";

xhr.open("POST", url, true);
xhr.setRequestHeader("Content-type", "application/json");
xhr.setRequestHeader('Access-Control-Allow-Origin','*');
xhr.onreadystatechange = function () { 
    if (xhr.readyState == 4 && xhr.status >= 200) {
        var json = JSON.parse(xhr.responseText);
        window.token = json['token'];
        console.log(json);
        window.localStorage.setItem('api_key',json.api_key);
        window.localStorage.setItem('client_id',json.client_id);
}
}   
xhr.send(data_user_register);
}


