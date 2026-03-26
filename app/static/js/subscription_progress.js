const startDateText = document.getElementById("start-date").textContent;
const [startDateDay, startDateMonth, startDateYear] = startDateText.split("-");
const startDate = new Date(startDateYear,startDateMonth-1,startDateDay);

const endDateText = document.getElementById("end-date").textContent;
const [endDateDay, endDateMonth, endDateYear] = endDateText.split("-");
const endDate = new Date(endDateYear,endDateMonth-1,endDateDay);

const today = new Date();

 // Calculate Days
 const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
 console.log(totalDays);
 const daysLeft = Math.max(0, Math.ceil((endDate - today) / (1000 * 60 * 60 * 24)));

 // Calculate Progress in Descending Order
 const progressWidth = (daysLeft / totalDays) * 100;

 // Update DOM
 document.getElementById("days-left").innerText = daysLeft;
 document.getElementById("total-days").innerText = totalDays;
//  document.getElementById("total-days-label").innerText = totalDays;

 // Update Progress Bar
 const progressBar = document.getElementById("progress-bar");
 const progressText = document.getElementById("progress-text");

 progressBar.style.width = `${progressWidth}%`;
 progressBar.setAttribute("aria-valuenow", daysLeft);

 // Display "X Days Left" Inside Progress Bar
 progressText.innerText = `${daysLeft} days left`;

 // Ensure text is visible when width is too small
//  if (progressWidth < 15) {
//    progressBar.classList.remove("text-white");
//    progressBar.classList.add("text-dark");
//  }