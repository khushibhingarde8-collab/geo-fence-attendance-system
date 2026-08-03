function fillJourney(id, year, title, description) {
  document.getElementById("journey_id").value = id;
  document.getElementById("journey_year").value = year;
  document.getElementById("journey_title").value = title;
  document.getElementById("journey_description").value = description;
}

function fillScope(id, title, description) {
  document.getElementById("scope_id").value = id;
  document.getElementById("scope_title").value = title;
  document.getElementById("scope_description").value = description;
}

function fillCertificate(id, title, description) {
  document.getElementById("certificate_id").value = id;
  document.getElementById("certificate_title").value = title;
  document.getElementById("certificate_description").value = description;
}

function fillNews(id, title, description, date, link) {
  document.getElementById("news_id").value = id;
  document.getElementById("news_title").value = title;
  document.getElementById("news_description").value = description;
  document.getElementById("news_date").value = date;
  document.getElementById("external_link").value = link;
}

function fillGallery(id, title, category) {
  document.getElementById("gallery_id").value = id;
  document.getElementById("gallery_title").value = title;
  document.getElementById("gallery_category").value = category;
}

function showSection(sectionId, element) {
  let sections = document.querySelectorAll(".section");

  sections.forEach((sec) => {
    sec.style.display = "none";
  });

  let activeSection = document.getElementById(sectionId);

  if (activeSection) {
    activeSection.style.display = "block";
  }

  // remove active class
  document.querySelectorAll("li").forEach((li) => {
    li.classList.remove("active");
  });

  // add active to clicked item
  if (element) {
    element.classList.add("active");
  }
}

function fillClient(id, name, website) {

    console.log("Client Edit:", id, name, website);

    document.getElementById("client_id").value = id;
    document.getElementById("client_name").value = name;
    document.getElementById("client_website").value = website || "";

}


function fillProjectPage(id, heading, description){
    document.getElementById("project_page_id").value = id;
    document.getElementById("project_heading").value = heading;
    document.getElementById("project_description").value = description;
}

function fillProjectCard(id, title, description, icon, slug){
    document.getElementById("card_id").value = id;
    document.getElementById("card_title").value = title;
    document.getElementById("card_description").value = description;
    document.getElementById("icon_class").value = icon;
    document.getElementById("slug").value = slug;
}

function fillProject(
id,
card_id,
title,
short_description,
full_description,
team_size,
duration,
technology_used,
client_name,
completion_date,
other_details
){

    document.getElementById("website_project_id").value = id;

    document.getElementById("project_card_id").value = card_id;

    document.getElementById("project_title").value = title;

    document.getElementById("short_description").value = short_description;

    document.getElementById("full_description").value = full_description;

    document.getElementById("team_size").value = team_size;

    document.getElementById("duration").value = duration;

    document.getElementById("technology_used").value = technology_used;

    document.getElementById("client_name_project").value = client_name;

    document.getElementById("completion_date").value = completion_date;

    document.getElementById("other_details").value = other_details;

}
