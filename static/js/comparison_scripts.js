var ratio = 0;
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
            ratio = Number(ajax.responseText);
        console.log("success");  
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

  $(document).ready(function() {  
     var chart = {
        type: 'spline',
        //animation: Highcharts.svg, // don't animate in IE < IE 10.
        marginRight: 10,
        events: {
           load: function () {
              // set up the updating of the chart each second
              var series = this.series[0];
              setInterval(function () {
                 var x = (new Date()).getTime(), // current time
                 //y = Math.floor(Math.random()*100)+1;
                 y = ratio;
                 console.log(y);
                 series.addPoint([x, y], true, true);
              }, 550);
           }
        }
     };
     var title = {
        text: '相似度曲線'   
     };   
     var xAxis = {
        type: 'datetime',
        tickPixelInterval: 150
     };
     var yAxis = {
        title: {
           text: '相似度百分比'
        },
        plotLines: [{
           value: 0,
           width: 1,
           color: '#808080'
        }]
     };
     var tooltip = {
        formatter: function () {
        return '<b>' + this.series.name + '</b><br/>' +
           Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
           Highcharts.numberFormat(this.y, 2);
        }
     };
     var plotOptions = {
        area: {
           pointStart: 1940,
           marker: {
              enabled: false,
              symbol: 'circle',
              radius: 2,
              states: {
                 hover: {
                   enabled: true
                 }
              }
           }
        }
     };
     var legend = {
        enabled: false
     };
     var exporting = {
        enabled: false
     };
     var series= [{
        name: 'Random data',
        data: (function () {
           // generate an array of random data
           var data = [],time = (new Date()).getTime(),i;
           for (i = -19; i <= 0; i += 1) {
              data.push({
                 x: time + i * 1000,
                 y: ratio
              });
           }
           return data;
        }())    
     }];     
        
     var json = {};   
     json.chart = chart; 
     json.title = title;     
     json.tooltip = tooltip;
     json.xAxis = xAxis;
     json.yAxis = yAxis; 
     json.legend = legend;  
     json.exporting = exporting;   
     json.series = series;
     json.plotOptions = plotOptions;
     
     
     Highcharts.setOptions({
        global: {
           useUTC: false
        }
     });
     $('#container').highcharts(json);
    
  });