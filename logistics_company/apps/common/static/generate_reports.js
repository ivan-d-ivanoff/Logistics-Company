$(document).ready(function() {
    $(document).on("click", ".clients_all", function(e) {
        e.preventDefault();

        const url = $(this).data("url");
        const csrf = $('#csrf-form input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            url: url,
            type: "GET",
            data: { csrfmiddlewaretoken: csrf },
            success: function(response) {
                console.log("Clients report generated successfully.", response);

                const clients = response.clients_report;

                let html = `<table border="1" style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Default Address</th>
                            <th>Prefered Address</th>
                        </tr>
                    </thead>
                    <tbody>`;

                clients.forEach(client => {
                    const defaultAddress = client.default_address || "-";
                    const preferedAddress = client.prefered_address || "-";

                    html += `<tr>
                        <td>${client.id}</td>
                        <td>${defaultAddress}</td>
                        <td>${preferedAddress}</td>
                    </tr>`;
                });

                html += `</tbody></table>`;

                $("#reportSubtitle").html(html);
            },
            error: function(xhr) {
                console.error("AJAX error:", xhr.responseText);
                $("#reportSubtitle").html("<p>Error loading report.</p>");
            },
        });
    });

    function generateParcelsReport(role) {
        // const clientId = $("#filterClient").val();
        // if (!clientId && role !== "all") {
        //     alert("Please select a client!");
        //     return;
        // }

        // only for testing
        const clientId = 3;

        let url = "";
        if (role === "all") {
            url = `/reports/client-parcels/all/`;
        } else {
            url = `/reports/client-parcels/${clientId}/${role}/`;
        }

        $.ajax({
            url: url,
            type: "GET",
            success: function(response) {
                console.log("Parcels report:", response);

                let html = `<table border="1" style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>Tracking Number</th>
                            <th>Status</th>
                            <th>Delivery Type</th>
                            <th>Price</th>
                            <th>Weight (kg)</th>
                            <th>Sender Client</th>
                            <th>Receiver Client</th>
                            <th>Sender Office</th>
                            <th>Receiver Office</th>
                            <th>Pickup Address</th>
                            <th>Delivery Address</th>
                            <th>Created At</th>
                            <th>Delivered At</th>
                        </tr>
                    </thead>
                    <tbody>`;

                response.parcels.forEach(p => {
                    html += `<tr>
                        <td>${p.tracking_number}</td>
                        <td>${p.status}</td>
                        <td>${p.delivery_type}</td>
                        <td>${p.price}</td>
                        <td>${p.weight_kg}</td>
                        <td>${p.sender_client}</td>
                        <td>${p.receiver_client}</td>
                        <td>${p.sender_office}</td>
                        <td>${p.receiver_office}</td>
                        <td>${p.pickup_address}</td>
                        <td>${p.delivery_address}</td>
                        <td>${p.created_at}</td>
                        <td>${p.delivered_at}</td>
                    </tr>`;
                });

                html += `</tbody></table>`;
                $("#reportSubtitle").html(html);
            },
            error: function(xhr) {
                console.error("AJAX error:", xhr.responseText);
                $("#reportSubtitle").html("<p>Error loading report.</p>");
            },
        });
    }

    $(document).on("click", ".client_sent", function() { 
        generateParcelsReport("sent"); 
    });

    $(document).on("click", ".client_received", function() { 
        generateParcelsReport("received"); 
    });

    $(document).on("click", ".parcels_all", function() { 
        generateParcelsReport("all"); 
    });

});
