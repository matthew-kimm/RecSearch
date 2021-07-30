# Tutorial
## Formatting the Data
A typical use case would have data from two tables, one table for user attributes and one table for user item ratings,
flattened into one table for use with the program.
* User Attribute Table
<table>
<tr>
  <th>User ID</th>
  <th>Attribute 1</th>
  <th>Attribute 2</th>
  <th>...</th>
</tr>
<tr>
  <td>1</td>
  <td>..</td>
  <td>..</td>
  <td>...</td>
</tr>
<tr>
  <td>2</td>
  <td>..</td>
  <td>..</td>
  <td>...</td>
</tr>
<tr>
  <td>...</td>
  <td>...</td>
  <td>...</td>
  <td>...</td>
</tr>
</table>

* User Item Rating Table
<table>
<tr>
  <th>User ID</th>
  <th>Item</th>
  <th>Rating</th>
  <th>Term</th>
</tr>
<tr>
  <td>1</td>
  <td>AAA</td>
  <td>2.3</td>
  <td>0</td>
</tr>
<tr>
  <td>1</td>
  <td>AAB</td>
  <td>2.7</td>
  <td>0</td>
</tr>
<tr>
  <td>1</td>
  <td>ABC</td>
  <td>3.3</td>
  <td>1</td>
</tr>
<tr>
  <td>1</td>
  <td>AAC</td>
  <td>1.7</td>
  <td>1</td>
</tr>
<tr>
  <td>2</td>
  <td>AAA</td>
  <td>4.0</td>
  <td>0</td>
</tr>
<tr>
  <td>...</td>
  <td>...</td>
  <td>...</td>
  <td>...</td>
</tr>
</table>
* Format Data Result
<table>
<tr>
  <th>User ID</th>
  <th>Item History</th>
  <th>Item Rating</th>
  <th>Attribute 1</th>
  <th>Attribute 2</th>
  <th>...</th>
</tr>
<tr>
  <td>1</td>
  <td>{'AAA': 2.3, 'AAB': 2.7}</td>
  <td>{'ABC': 3.3, 'AAC': 1.7}</td>
  <td>..</td>
  <td>..</td>
  <td>...</td>
</tr>
<tr>
  <td>2</td>
  <td>{'AAA': 4.0, ..}</td>
  <td>..</td>
  <td>..</td>
  <td>..</td>
  <td>...</td>
</tr>
<tr>
  <td>...</td>
  <td>...</td>
  <td>...</td>
  <td>...</td>
  <td>...</td>
  <td>...</td>
</tr>
</table>

The Item Rating column is the column storing the target ratings used by the recommender whereas the Item History column
is used for finding neighbors. If your data has the same headings as
the User Item Rating Table with IDs linked to an attribute table,
then navigate to `Tools > Format Data` in the GUI to flatten the data.

(Demo)