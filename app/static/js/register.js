let registerButton = document.getElementById("register_button")
let idData = document.getElementById("register_id")
let nameData = document.getElementById("register_name")
let fullNameData = document.getElementById("register_full_name")
let cameraEl = document.getElementById("camera-server")
registerButton.onclick = async (e) => {
    e.preventDefault()
    let id = idData.value
    let name = nameData.value
    let fullName = fullNameData.value
    let data = {
        idData: id,
        nameData: name,
        fullNameData: fullName
    }
    fetch("/register_new", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    })
}