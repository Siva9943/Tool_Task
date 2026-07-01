document.querySelectorAll('.toast').forEach(toastEl => {
    setTimeout(() => {
        let toast = new bootstrap.Toast(toastEl);
        toast.hide();
    }, 3000);
});

toastr.success("File uploaded successfully");
toastr.error("Invalid file type");