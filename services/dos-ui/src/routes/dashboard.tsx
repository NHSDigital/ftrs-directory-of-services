import { createFileRoute, redirect, useLoaderData } from "@tanstack/react-router";
import {SessionManager, setupSessionFn} from "@/core/session";
import { useClientSession } from "@/core/context";
import type { UserInfo } from "@/core/schema";



export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
  head: () => ({
    meta: [{ title: "Dashboard - FtRS DoS UI" }],
  }),
  loader: async ({ context }) => {
    if (!context.session) {
      context.session = await setupSessionFn();
    }

    if (!context.session.sessionID) {
      throw redirect({ to: "/" });
    }

    const manager = new SessionManager();
    const userSession = await manager.getSession(context.session.sessionID);

    if (!userSession || !userSession.user) {
      throw redirect({ to: "/" });
    }

    return {
      user: userSession.user,
    };
  },
});

function DashboardPage() {
  const session = useClientSession();
  const { user } = useLoaderData({ from: "/dashboard" });

  return (
    <div className="nhsuk-width-container">
      <main className="nhsuk-main-wrapper" >
        <div className="nhsuk-grid-row">
          <div className="nhsuk-grid-column-full">
            <h1 className="nhsuk-heading-xl">Dashboard</h1>

            <div className="nhsuk-card">
              <div className="nhsuk-card__content">
                <h2 className="nhsuk-heading-m">User Information</h2>
                <dl className="nhsuk-summary-list">
                  <div className="nhsuk-summary-list__row">
                    <dt className="nhsuk-summary-list__key">Name</dt>
                    <dd className="nhsuk-summary-list__value">{user.displayName}</dd>
                  </div>
                  <div className="nhsuk-summary-list__row">
                    <dt className="nhsuk-summary-list__key">User ID</dt>
                    <dd className="nhsuk-summary-list__value">{user.uid}</dd>
                  </div>
                  <div className="nhsuk-summary-list__row">
                    <dt className="nhsuk-summary-list__key">Selected Role ID</dt>
                    <dd className="nhsuk-summary-list__value">{user.selectedRoleID}</dd>
                  </div>
                </dl>
              </div>
            </div>

            {user.rbacRoles && user.rbacRoles.length > 0 && (
              <div className="nhsuk-card">
                <div className="nhsuk-card__content">
                  <h2 className="nhsuk-heading-m">RBAC Roles</h2>
                  <table className="nhsuk-table">
                    <thead className="nhsuk-table__head">
                    <tr className="nhsuk-table__row">
                      <th className="nhsuk-table__header" scope="col">Role Name</th>
                      <th className="nhsuk-table__header" scope="col">Organisation Code</th>
                      <th className="nhsuk-table__header" scope="col">Person Role ID</th>
                    </tr>
                    </thead>
                    <tbody className="nhsuk-table__body">
                    {user.rbacRoles.map((role: UserInfo['rbacRoles'][number]) => (
                      <tr key={role.personRoleID} className="nhsuk-table__row">
                        <td className="nhsuk-table__cell">{role.roleName}</td>
                        <td className="nhsuk-table__cell">{role.orgCode}</td>
                        <td className="nhsuk-table__cell">{role.personRoleID}</td>
                      </tr>
                    ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {user.orgMemberships && user.orgMemberships.length > 0 && (
              <div className="nhsuk-card">
                <div className="nhsuk-card__content">
                  <h2 className="nhsuk-heading-m">Organisation Memberships</h2>
                  <table className="nhsuk-table">
                    <thead className="nhsuk-table__head">
                    <tr className="nhsuk-table__row">
                      <th className="nhsuk-table__header" scope="col">Organisation Name</th>
                      <th className="nhsuk-table__header" scope="col">Organisation Code</th>
                    </tr>
                    </thead>
                    <tbody className="nhsuk-table__body">
                    {user.orgMemberships.map((org: UserInfo['orgMemberships'][number]) => (
                      <tr key={org.orgCode} className="nhsuk-table__row">
                        <td className="nhsuk-table__cell">{org.orgName}</td>
                        <td className="nhsuk-table__cell">{org.orgCode}</td>
                      </tr>
                    ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {user.userOrgs && user.userOrgs.length > 0 && (
              <div className="nhsuk-card">
                <div className="nhsuk-card__content">
                  <h2 className="nhsuk-heading-m">User Organisations</h2>
                  <table className="nhsuk-table">
                    <thead className="nhsuk-table__head">
                    <tr className="nhsuk-table__row">
                      <th className="nhsuk-table__header" scope="col">Organisation Name</th>
                      <th className="nhsuk-table__header" scope="col">Organisation Code</th>
                    </tr>
                    </thead>
                    <tbody className="nhsuk-table__body">
                    {user.userOrgs.map((org: UserInfo['userOrgs'][number]) => (
                      <tr key={org.orgCode} className="nhsuk-table__row">
                        <td className="nhsuk-table__cell">{org.orgName}</td>
                        <td className="nhsuk-table__cell">{org.orgCode}</td>
                      </tr>
                    ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="nhsuk-card">
              <div className="nhsuk-card__content">
                <h2 className="nhsuk-heading-m">Session Information</h2>
                <dl className="nhsuk-summary-list">
                  <div className="nhsuk-summary-list__row">
                    <dt className="nhsuk-summary-list__key">Session ID</dt>
                    <dd className="nhsuk-summary-list__value">{session.sessionID}</dd>
                  </div>
                  <div className="nhsuk-summary-list__row">
                    <dt className="nhsuk-summary-list__key">Expires At</dt>
                    <dd className="nhsuk-summary-list__value">
                      {new Date(session.expiresAt).toLocaleString()}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
