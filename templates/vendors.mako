<%inherit file="base.html" />

<%block name="header">
    <h1>D.C. Food Trucks</h1>
</%block>

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Site Permit</th>
            <th>Alias</th>
        </tr>
    </thead>
    <tbody>
        % for vendor in vendors:
            <tr id="${vendor['id']}">
                <td>${vendor['name']}</td>
                <td>${vendor['site_permit']}</td>
                <td>${vendor['alias']}</td>
            </tr>
        % endfor
    </tbody>
</table>

<div class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <form>
            <input type="text" id="vendorName" placeholder="Name" />
            <input type="text" id="vendorId" />
            <input type="submit" id="submit" value="Update Vendor" />
        </form>
    </div>
</div>
