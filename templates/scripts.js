var display_video_name = "VIDEO0068.mp4"

function GetData(){
    var text = document.getElementById("similarity_value");
    
    var url = "/get_ratio";  
    var ajax = false;  

    //開始初始化XMLHttpRequest物件  
    if(window.XMLHttpRequest)   
    {   //Mozilla 瀏覽器
        ajax = new XMLHttpRequest();  
        if (ajax.overrideMimeType)   
        {   //設定MiME類別  
            ajax.overrideMimeType("text/xml");  
        }  
    }  
    else if (window.ActiveXObject)   
    {   // IE瀏覽器  
        try   
        {  
            ajax = new ActiveXObject("Msxml2.XMLHTTP");  
        }   
        catch (e)   
        {  
            try   
            {  
                ajax = new ActiveXObject("Microsoft.XMLHTTP");  
            }   
            catch (e) {}  
        }  
    }  
    if (!ajax)   
    {   // 異常，建立物件例項失敗  
        window.alert("不能建立XMLHttpRequest物件例項.");  
        return false;  
    }  
                    
    
    //通過Post方式開啟連線  
    ajax.open("GET", url, true);  
    console.log("開啟連線");
    ajax.send();

    //獲取執行狀態  
    ajax.onreadystatechange = function()
    {
    console.log("以獲取執行狀態");
        // 如果執行狀態成功，那麼就把返回資訊寫到指定的層裡  
        if (ajax.readyState == 4 && ajax.status == 200)   
        {   
            text.innerHTML = ajax.responseText; 
        conosle.log("success");  
        }   
    }   
}

function doUpdate()   
{
    console.log("開始跑doUpdate");
    GetData();
    window.setTimeout("doUpdate()", 100);
}
console.log("go");
doUpdate();
console.log("end");