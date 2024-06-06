//這邊連線的網址應該要改成我們線上環境的IP位置嗚嗚！
//然後API的檔案接受的來源也要改一下
// http://44.230.128.247:8000/api/attractions
// http://127.0.0.1:8000/api/attractions?page=0

let main_layout=document.querySelector(".main_layout");
let detection_point=document.querySelector(".detection_point");

//這是用來各種創建標籤節點的函式
let create_and_append=(parent,tag,className,text)=>{  //這邊創建函式的方法一定要好好學起來
    let element=document.createElement(tag);
    if (className){
        element.classList.add(className);
    }
    element.textContent=text;
    parent.appendChild(element);
    return element;  //當初有卡住，但壞掉王說要加入return，確實加了就好了，邏輯再順一次！
}


//這是用來真的創建我的那12個景點資訊的函式
let create_attraction_section=(data)=>{

    let data_count=data.data.length
    let newSection=document.createElement("section");

    if (data_count>=1 && data_count<=4){
        newSection.className="section_sheard section_layout_for_one_to_four"
    }
    else if(data_count<=8){
        newSection.className="section_sheard section_layout_for_one_to_eight"
    }
    else if(data_count<=12){
        newSection.className="section_sheard section_layout_for_one_to_twelve"
    }
   

    for (attraction of data.data ){
    
        let newArticle=create_and_append(newSection,"article","","")
        let newDiv1=create_and_append(newArticle, "div", "name_and_image_layout", "");
        let newDiv2=create_and_append(newArticle, "div", "station_and_category", "");
        
        let newFigure=create_and_append(newDiv1,"figure","","");
        let newImg=create_and_append(newFigure,"img","attraction_image","");
        newImg.src=attraction.images[0];

        let newFigcaption=create_and_append(newDiv1,"figcaption","","");
        let newAttractionName=create_and_append(newFigcaption,"div","attraction_name",attraction.name);

        let newAttractionStation=create_and_append(newDiv2,"div","attraction_station",attraction.mrt);
        let newAttractionCategory=create_and_append(newDiv2,"div","attraction_category",attraction.category);

        main_layout.insertBefore(newSection,detection_point); //一律都在偵測點前，建立那十二個景點
    }


    //以下為原版本，以防萬一保存起來怕怕
    // let newSection=document.createElement("section");
    // newSection.className="section_layout"

    // for (attraction of data.data ){
    
    //     let newArticle=create_and_append(newSection,"article","","")
    //     let newDiv1=create_and_append(newArticle, "div", "name_and_image_layout", "");
    //     let newDiv2=create_and_append(newArticle, "div", "station_ang_category", "");
        
    //     let newFigure=create_and_append(newDiv1,"figure","","");
    //     let newImg=create_and_append(newFigure,"img","attraction_image","");
    //     newImg.src=attraction.images[0];

    //     let newFigcaption=create_and_append(newDiv1,"figcaption","","");
    //     let newAttractionName=create_and_append(newFigcaption,"div","attraction_name",attraction.name);

    //     let newAttractionStation=create_and_append(newDiv2,"div","attraction_station",attraction.mrt);
    //     let newAttractionCategory=create_and_append(newDiv2,"div","attraction_category",attraction.category);

    //     main_layout.insertBefore(newSection,detection_point); //一律都在偵測點前，建立那十二個景點
    // }

}



// async function fetch_attractions(){ //這是在連線這塊，使用async/await的方法，我後來沒用啦，但反正蠻不錯的，也需要學一下
//     try{
//         let response=await fetch("http://127.0.0.1:8000/api/attractions?page=0")
//         if (!response.ok){
//             throw new Error("API request failed")
//         }
//         let data=await response.json();

//         create_attraction_section(data);

//         return data.nextPage;
//     }
//     catch(error){console.error(error)}
// }

// document.addEventListener("DOMContentLoaded",
//     async function(){
//         fetch_attractions()
//     }
// )
    


fetch("http://44.230.128.247:8000/api/attractions?page=0")
.then(response => {
    if (response.ok){return response.json()}
    else {throw new Error("API request failed")}
})
.then(data => {
    create_attraction_section(data);
    handle_nextPage(data.nextPage);

    // console.log(data)
    // console.log(data.data)
    // console.log(data.nextPage)

})
.catch(error => {console.error(error)})


let handle_nextPage=(nextPage)=>{
    // 在這裡處理 nextPage，發出下一頁的請求
    
    if (nextPage !==null){ //如果nextPage，不是空值，我們才建立監聽事件
        let observer= new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting){

                    //如果視窗跟偵測點接觸了 －－－>應該要再進行連線取得下一頁的資料＋渲染，直到沒有資料為止
                    fetch(`http://44.230.128.247:8000/api/attractions?page=${nextPage}`)
                    .then(response => {
                        if (response.ok){return response.json()}
                        else {throw new Error("API request failed")}
                    })
                    .then(data => {
                        create_attraction_section(data);
                        observer.unobserve(detection_point); //這個邏輯可能要再順一次，目前卡在啊我新景點加入了，但沒有進入視窗範圍啊，不懂為何會無限觸發

                        handle_nextPage(data.nextPage);
                    })
                    .catch(error => {console.error(error)})
                }
            })
        })
        observer.observe(detection_point);
    }
}




