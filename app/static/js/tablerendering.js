document.addEventListener("DOMContentLoaded", function() {
    let isCameraActive = false;
    let intervalId = null;
    let cameraElement = document.getElementById('camera-feed');
    let backgroundImageElement = document.getElementById('background-image'); // Giả sử bạn có thêm một element cho hình nền
    // function fetchAndDisplayStudents() {
    //     fetch('/StudentChecking')
    //         .then(response => response.json())
    //         .then(data => {
    //             let tableBody = document.getElementById('studentTableBody');
    //             tableBody.innerHTML = ''; // Xóa nội dung cũ
    //             Object.values(data).forEach((student, index) => {
    //                 let timestamp = new Date().getTime(); // Thời gian hiện tại để tránh cache
    //                 let row = `<tr>
    //                                <th scope="row">${index + 1}</th>
    //                                <td>${student.StudentID}</td>
    //                                <td>${student.FullName}</td>
    //                                <td><img src="${student.Avatar}?t=${timestamp}" alt="Avatar" style="width:50px;height:50px;"></td>
    //                                <td>${student.CheckInTime}</td>
    //                                <td><img src="${student.CheckInImage}?t=${timestamp}" alt="Check-In" style="width:50px;height:50px;"></td>
    //                                <td>${student.CheckOutTime}</td>
    //                                <td><img src="${student.CheckOutImage}?t=${timestamp}" alt="Check-Out" style="width:50px;height:50px;"></td>
    //                                <td>${student.HandRissing}</td>
    //                                <td>${student.Status}</td>
    //                            </tr>`;
    //                 tableBody.innerHTML += row;
    //             });
    //         })
    //         .catch(error => console.error('Error:', error));
    // }

    // function initializeData() {
    //     fetch('/initdata')
    //         .then(response => response.json())
    //         .then(data => {
    //             let tableBody = document.getElementById('studentTableBody');
    //             tableBody.innerHTML = ''; // Xóa nội dung cũ
    //             Object.values(data).forEach((student, index) => {
    //                 let timestamp = new Date().getTime(); // Thời gian hiện tại để tránh cache
    //                 let row = `<tr>
    //                             <th scope="row">${index + 1}</th>
    //                             <td>${student.StudentID}</td>
    //                             <td>${student.FullName}</td>
    //                             <td><img src="${student.Avatar}?t=${timestamp}" alt="Avatar" style="width:50px;height:50px;"></td>
    //                             <td>${student.CheckInTime}</td>
    //                             <td><img src="${student.CheckInImage}?t=${timestamp}" alt="Check-In" style="width:50px;height:50px;"></td>
    //                             <td>${student.CheckOutTime}</td>
    //                             <td><img src="${student.CheckOutImage}?t=${timestamp}" alt="Check-Out" style="width:50px;height:50px;"></td>
    //                             <td>${student.HandRissing}</td>
    //                             <td>${student.Status}</td>
    //                         </tr>`;
    //                 tableBody.innerHTML += row;
    //             });
    //         })
    //         .catch(error => console.error('Error:', error));
    // }

    // function toggleCameraAndBackground() {
    //     isCameraActive = !isCameraActive;
    
    //     if (isCameraActive) {
    //         // Bật camera
    //         cameraElement.style.display = "block";
    //         backgroundImageElement.style.display = "none";
    //         if (intervalId === null) {
    //             // intervalId = setInterval(fetchAndDisplayStudents, 3000); // Cập nhật mỗi 3 giây
    //             intervalId = setInterval(updatePeopleData, 3000); // Cập nhật mỗi 3 giây
    //         }
    //     } else {
    //         // Tắt camera
    //         cameraElement.style.display = "none";
    //         backgroundImageElement.style.display = "block";
    
    //         if (intervalId !== null) {
    //             clearInterval(intervalId);
    //             intervalId = null;
    //         }
    //     }
    // }

    function createTableRow(data, index) {
        let row = document.createElement("tr")
        let th = document.createElement("th")
        th.textContent = parseInt(index) + 1
        row.appendChild(th)
        let keyOrder = ["id", "full_name", "avatar", "attendance", "time"]
        for (let key of keyOrder) {
            let value = data[key]
            let td = document.createElement("td");
            if (key == "avatar") {
                let imgEl = document.createElement("img")
                imgEl.src = value
                imgEl.style.width = "50px"
                imgEl.style.height = "50px"
                td.appendChild(imgEl)
            } else if (key == "attendance") {
                value = value ? "Present" : "Absent"
                td.textContent = value
            } else if (key == "time") {
                value = value ? new Date(value.time).toISOString() : "NULL"
                td.textContent = value
            } else {
                td.textContent = value
            }
            row.appendChild(td)
        }
        return row
    }

    async function updatePeopleData() {
        let tbody = document.getElementById('studentTableBody')
        let res = await fetch("/peopleData")
        let people = await res.json()
        people = people.data
        tbody.innerHTML = ''
        for (let i in people) {
            let person = people[i]
            let row = createTableRow(person, i)
            tbody.appendChild(row)
        }
    }

    updatePeopleData()
    setInterval(updatePeopleData, 3000)

    // Cài đặt sự kiện cho nút bật/tắt camera
    document.getElementById("toggleCameraBtn").addEventListener("click", function() {
        toggleCameraAndBackground();
    });

    // Luôn hiển thị bảng và khởi tạo dữ liệu
    document.getElementById("student-list").style.display = "block";
    // initializeData();
    fetchAndDisplayStudents(); // Nếu bạn muốn bảng được cập nhật ngay lập tức

    // Đặt camera để không hiển thị và hình nền hiển thị khi trang được tải
    cameraElement.style.display = "none";
    backgroundImageElement.style.display = "block";
});


