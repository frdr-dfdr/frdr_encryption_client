# FRDR Encryption App

## REST API Sample Code (Java)

```
@Path("/")
public class RestAPI
{
    private static final Logger log = LogManager.getLogger(RestAPI.class);

    /**
     * Find the item by the value of the "frdr.vault.dataset_uuid" metadata field.
     */
    private Item findItemByVaultDatasetId(Context context, String vaultDatasetId, int accessMode)
            throws SQLException, AuthorizeException, IOException
    {
        ItemIterator itemIterator = Item.findByMetadataField(context, FRDR.schema, FRDR.vault, FRDR.dataset_uuid, vaultDatasetId);

        Item item = null;
        while (itemIterator.hasNext()) {
            item = itemIterator.next();
            if (itemIterator.hasNext()) {
                throw new WebApplicationException(
                    buildResponse(Status.BAD_REQUEST, "More than one dataset with metadata frdr.vault.dataset_uuid " + vaultDatasetId + " was found"));
            }
        }
        if (item == null) {
            throw new WebApplicationException(
                buildResponse(Status.NOT_FOUND, "Dataset with metadata frdr.vault.dataset_uuid" + vaultDatasetId + " not found"));
        }

        AuthorizeManager.authorizeAction(context, item, accessMode);
        return item;
    }

    /**
     * Find the requestItem by ID.
     */
    private RequestItem findRequestItem(Context context, int requestItemId)
            throws SQLException, AuthorizeException
    {
        RequestItem req = RequestItem.find(context, requestItemId);
        if (req == null) {
            throw new WebApplicationException(buildResponse(Status.NOT_FOUND, "RequestItem " + requestItemId + " not found"));
        }

        EPerson apiUser = context.getCurrentUser();
        Item item = req.getItem();
        EPerson reqSubmitter = null;
        if (item != null) {
            reqSubmitter = item.getSubmitter();
        }
        EPerson reqRequester = req.getRequester();
        if (apiUser == null) {
            throw new AuthorizeException("Authorization credentials were not supplied or expired");
        } else if (!apiUser.equals(reqSubmitter) && !apiUser.equals(reqRequester) && !AuthorizeManager.isStaff(context)) {
            throw new AuthorizeException("Authorization denied - you must be the depositor or requester to view this requestitem");
        }

        return req;
    }

    /**
     *  Find the requestitem by the value of the "frdr.vault.dataset_uuid" metadata field 
     *  and the value of "frdr.vault.dataset_uuid" metadata field.
     */
    private RequestItem findRequestItemByDatasetVaultIdAndRequesterVaultId(Context context, String vaultDatasetId, String vaultRequesterId, String status)
        throws SQLException, AuthorizeException, Exception
    {
        ItemIterator itemIterator = Item.findByMetadataField(context, FRDR.schema, FRDR.vault, FRDR.dataset_uuid, vaultDatasetId);
        Item item = null;
        while (itemIterator.hasNext()) {
            item = itemIterator.next();
            if (itemIterator.hasNext()) {
                throw new WebApplicationException(
                    buildResponse(Status.BAD_REQUEST, "More than one dataset with metadata frdr.vault.dataset_uuid " + vaultDatasetId + " was found"));
            }
        }
        if (item == null) {
            throw new WebApplicationException(
                buildResponse(Status.NOT_FOUND, "Dataset with metadata frdr.vault.dataset_uuid" + vaultDatasetId + " not found"));
        }

        RequestItem req = RequestItem.FindRequestByItemAndRequesterVaultId(context, item, vaultRequesterId, status);
        if (req == null) {
            throw new WebApplicationException(
                buildResponse(Status.NOT_FOUND, "RequestItem in status of " + status + ", with vault_dataset_id " + vaultDatasetId + " and vault_requester_id " + vaultRequesterId + " not found"));
        }

        EPerson apiUser = context.getCurrentUser();
        EPerson itemSubmitter = null;
        if (item != null) {
            itemSubmitter = item.getSubmitter();
        }

        EPerson reqRequester = req.getRequester();
        
        if (apiUser == null) {
            throw new AuthorizeException("Authorization credentials were not supplied or expired");
        } else if (status.equals(RequestItem.STATUS_PENDING_WITH_DEPOSITOR) && !apiUser.equals(itemSubmitter) && !AuthorizeManager.isStaff(context)) {
            throw new AuthorizeException("Authorization denied - you must be the depositor to update this requestitem");
        } else if (status.equals(RequestItem.STATUS_GRANTED) && !apiUser.equals(reqRequester) && !AuthorizeManager.isStaff(context)) {
            throw new AuthorizeException("Authorization denied - you must be the requester to update this requestitem");
        }

        return req;
    }    

    private Response handleException(Context context, Exception e)
    {
        if (context != null) {
            context.abort();
        }
        if (e instanceof WebApplicationException) {
            throw (WebApplicationException) e;
        } else if (e instanceof AuthorizeException) {
            log.info("Failed to authorize action on " + e);
            throw new WebApplicationException(buildResponse(Status.FORBIDDEN, "Not allowed"));
        } else {
            log.error("RestAPI raising a 500 due to:", e);
            throw new WebApplicationException(buildResponse(Status.INTERNAL_SERVER_ERROR, 
                                                            e.getMessage()));
        }
    }

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    @Path("/requestitem/{requestitem_id}")
    public Response getRequestItemById(@PathParam("requestitem_id") Integer requestItemId,
                                   @HeaderParam("Authorization") String auth,
                                   @javax.ws.rs.core.Context HttpServletRequest request)
        throws WebApplicationException
    {
        RequestItem req = null;
        Context context = null;
        try {
            context = getContextForAuthUser(auth, true, Context.READ_ONLY);
            req = findRequestItem(context, requestItemId);
            JSONObject requestitemJson = requestitemToJson(req);
            context.complete();
            context = null;
            return buildResponse(Status.OK, requestitemJson);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }

    @GET
    @Path("/requestitem/grant-access/verify")
    public Response getSubmissions(@QueryParam("vault_dataset_id") String vaultDatasetId,
                                @QueryParam("vault_requester_id") String vaultRequesterId,
                                @HeaderParam("Authorization") String auth)
        throws WebApplicationException
    {
        RequestItem req = null;
        Context context = null;
        try {
            context = getContextForAuthUser(auth, false, (short) 0);
            req = findRequestItemByDatasetVaultIdAndRequesterVaultId(context, vaultDatasetId, vaultRequesterId, RequestItem.STATUS_PENDING_WITH_DEPOSITOR);
            Date now = new Date();
            // If access to the key has been granted
            if (req.getKeyExpireDate() != null && req.getKeyExpireDate().after(now)) {
                throw new WebApplicationException(buildResponse(Status.NOT_FOUND, "Access to the key has been granted"));
            }
            JSONObject requestitemJson = requestitemToJson(req);
            context.complete();
            context = null;
            return buildResponse(Status.OK, requestitemJson);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }

    @PUT
    @Path("/requestitem/grant-access")
    public Response updateRequestItemGrantAccess(@HeaderParam("Authorization") String auth,
                                     String input)
        throws WebApplicationException
    {
        RequestItem req = null;
        Context context = null;
        try {
            context = getContextForAuthUser(auth, false, (short) 0);
            JSONObject body = new JSONObject(input);
            String expireStr = body.getString("expires");
            String vaultDatasetId = body.getString("vault_dataset_id");
            String vaultRequesterId = body.getString("vault_requester_id");
            req = findRequestItemByDatasetVaultIdAndRequesterVaultId(context, vaultDatasetId, vaultRequesterId, RequestItem.STATUS_PENDING_WITH_DEPOSITOR);
            req.setGrantedOnVault(true);
            Date expireDate = new SimpleDateFormat(Constants.DATE_FORMAT_YYYYMMDD).parse(expireStr);
            Date endOfExpireDate = Utils.getEndOfDay(expireDate);
            req.setKeyExpireDate(endOfExpireDate);
            req.update();
            JSONObject requestitemJson = requestitemToJson(req);
            context.complete();
            context = null;
            return buildResponse(Status.OK, requestitemJson);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }

    @PUT
    @Path("/requestitem/decrypt")
    public Response updateRequestItemDecrypt(@HeaderParam("Authorization") String auth,
                                     String input)
        throws WebApplicationException
    {
        RequestItem req = null;
        Context context = null;
        try {
            context = getContextForAuthUser(auth, false, (short) 0);
            JSONObject body = new JSONObject(input);
            String vaultDatasetId = body.getString("vault_dataset_id");
            String vaultRequesterId = body.getString("vault_requester_id");
            req = findRequestItemByDatasetVaultIdAndRequesterVaultId(context, vaultDatasetId, vaultRequesterId, RequestItem.STATUS_GRANTED);
            req.setLastDecrypted(new Date());
            req.update();
            JSONObject requestitemJson = requestitemToJson(req);
            context.complete();
            context = null;
            return buildResponse(Status.OK, requestitemJson);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    @Path("/dataset-title/{vault_dataset_id}")
    public Response getDatasetTitleByVaultDatasetId(@PathParam("vault_dataset_id") String vaultDatasetId,
                                                    @QueryParam("format") String exportFormat,
                                                    @HeaderParam("Authorization") String auth,
                                                    @javax.ws.rs.core.Context HttpServletRequest request)
        throws WebApplicationException
    {
        Item item = null;
        Context context = null;
        try {
            context = getContextForAuthUser(auth, true, Context.READ_ONLY);
            item = findItemByVaultDatasetId(context, vaultDatasetId, Constants.READ);
            // item title
            String title = item.getTitle(null);
            JSONObject jo = new JSONObject();
            jo.put("dataset_title", title);
            context.complete();
            context = null;
            return buildResponse(Status.OK, jo);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    @Path("/uservaultid")
    public Response getCurrentUserVaultId(@HeaderParam("Authorization") String auth,
                                          @javax.ws.rs.core.Context HttpServletRequest request)
        throws WebApplicationException
    {
        Item item = null;
        Context context = null;
        try {
            context = getContextForAuthUser(auth, false, (short) 0);
            String vaultId = context.getCurrentUser().getVaultId();
            if (vaultId == null) {
                vaultId = "";
            }
            JSONObject jo = new JSONObject();
            jo.put("user_vault_id", vaultId);
            context.complete();
            context = null;
            return buildResponse(Status.OK, jo);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }

    @PUT
    @Path("/uservaultid")
    public Response getCurrentUserVaultId(@HeaderParam("Authorization") String auth,
                                          String input)
        throws WebApplicationException
    {
        Context context = null;
        try {
            context = getContextForAuthUser(auth, false, (short) 0);
            JSONObject body = new JSONObject(input);
            String vaultId = body.getString("user_vault_id");
            EPerson currentUser = context.getCurrentUser();
            currentUser.setVaultId(vaultId);
            currentUser.update();
            JSONObject jo = new JSONObject();
            jo.put("user_vault_id", vaultId);
            context.complete();
            context = null;
            return buildResponse(Status.OK, jo);
        } catch (Exception e) {
            return handleException(context, e);
        }
    }

    /**
     * @param req The RequestItem to query
     * @return A JSON object containing the RequestItem details
     */
    private JSONObject requestitemToJson(RequestItem req)
    {
        String expireDatestring = req.getKeyExpireDateSimple();
        JSONObject jo = new JSONObject();
        jo.put("id", req.getID());
        jo.put("expires", expireDatestring);
        return jo;
    }

    /**
     * @param httpAuthorizationHeader
     * @param allowAnon
     * @param contextOptions
     * @return
     * @throws SQLException
     * @throws AuthorizeException 
     */
    private Context getContextForAuthUser(String httpAuthorizationHeader, boolean allowAnon, short contextOptions)
        throws SQLException, WebApplicationException, AuthorizeException
    {
        Context ctx = new Context(contextOptions);
        GlobusAuthToken authToken = null;
        try {
            authToken = getAuthTokenForHttpAuthorizationHeader(httpAuthorizationHeader, true, true);
        } catch (GlobusClientException gce) {
            // We'll pass through to null check on subjectId
        }
        if (authToken == null && !allowAnon) {
            throw new WebApplicationException(buildResponse(Status.FORBIDDEN, "Not authorized"));
        }
        if (authToken != null) {
            EPerson ep = null;
            try {
                ep = GlobusAuthAuthentication.getEPersonForAuthToken(ctx, authToken, true, null);
            } catch (IllegalStateException ise) {
                // Needed to create a new user, but we had a readonly context so that fails.
                log.info("EPerson lookup failed due to readonly context, retrying");
                Context newuserCtx = new Context();
                ep = GlobusAuthAuthentication.getEPersonForAuthToken(newuserCtx, authToken, true, null);
                newuserCtx.complete();
            }
            if (ep != null) {
                String displayId = ep.getEmail();
                if (displayId == null) {
                    displayId = ep.getNetid();
                }
                log.info("Authenticated user " + displayId + " for API usage");
                ctx.setCurrentUser(ep);
            } else {
                log.error("REST API authenticated user, but user was not in local eperson table");
            }
            Globus g = new Globus(authToken);
            Globus.addGlobusClientToContext(g, ctx);
        }
        return ctx;
    }
}
```
